```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.securityinsight

    class azure.mgmt.securityinsight.SecurityInsights: implements ContextManager 
        actions: ActionsOperations
        alert_rule_templates: AlertRuleTemplatesOperations
        alert_rules: AlertRulesOperations
        automation_rules: AutomationRulesOperations
        bookmark: BookmarkOperations
        bookmark_relations: BookmarkRelationsOperations
        bookmarks: BookmarksOperations
        data_connectors: DataConnectorsOperations
        data_connectors_check_requirements: DataConnectorsCheckRequirementsOperations
        domain_whois: DomainWhoisOperations
        entities: EntitiesOperations
        entities_get_timeline: EntitiesGetTimelineOperations
        entities_relations: EntitiesRelationsOperations
        entity_queries: EntityQueriesOperations
        entity_query_templates: EntityQueryTemplatesOperations
        entity_relations: EntityRelationsOperations
        file_imports: FileImportsOperations
        get: GetOperations
        get_recommendations: GetRecommendationsOperations
        incident_comments: IncidentCommentsOperations
        incident_relations: IncidentRelationsOperations
        incident_tasks: IncidentTasksOperations
        incidents: IncidentsOperations
        ip_geodata: IPGeodataOperations
        metadata: MetadataOperations
        office_consents: OfficeConsentsOperations
        operations: Operations
        product_settings: ProductSettingsOperations
        security_ml_analytics_settings: SecurityMLAnalyticsSettingsOperations
        sentinel_onboarding_states: SentinelOnboardingStatesOperations
        source_control: SourceControlOperations
        source_controls: SourceControlsOperations
        threat_intelligence_indicator: ThreatIntelligenceIndicatorOperations
        threat_intelligence_indicator_metrics: ThreatIntelligenceIndicatorMetricsOperations
        threat_intelligence_indicators: ThreatIntelligenceIndicatorsOperations
        update: UpdateOperations
        watchlist_items: WatchlistItemsOperations
        watchlists: WatchlistsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.securityinsight.aio

    class azure.mgmt.securityinsight.aio.SecurityInsights: implements AsyncContextManager 
        actions: ActionsOperations
        alert_rule_templates: AlertRuleTemplatesOperations
        alert_rules: AlertRulesOperations
        automation_rules: AutomationRulesOperations
        bookmark: BookmarkOperations
        bookmark_relations: BookmarkRelationsOperations
        bookmarks: BookmarksOperations
        data_connectors: DataConnectorsOperations
        data_connectors_check_requirements: DataConnectorsCheckRequirementsOperations
        domain_whois: DomainWhoisOperations
        entities: EntitiesOperations
        entities_get_timeline: EntitiesGetTimelineOperations
        entities_relations: EntitiesRelationsOperations
        entity_queries: EntityQueriesOperations
        entity_query_templates: EntityQueryTemplatesOperations
        entity_relations: EntityRelationsOperations
        file_imports: FileImportsOperations
        get: GetOperations
        get_recommendations: GetRecommendationsOperations
        incident_comments: IncidentCommentsOperations
        incident_relations: IncidentRelationsOperations
        incident_tasks: IncidentTasksOperations
        incidents: IncidentsOperations
        ip_geodata: IPGeodataOperations
        metadata: MetadataOperations
        office_consents: OfficeConsentsOperations
        operations: Operations
        product_settings: ProductSettingsOperations
        security_ml_analytics_settings: SecurityMLAnalyticsSettingsOperations
        sentinel_onboarding_states: SentinelOnboardingStatesOperations
        source_control: SourceControlOperations
        source_controls: SourceControlsOperations
        threat_intelligence_indicator: ThreatIntelligenceIndicatorOperations
        threat_intelligence_indicator_metrics: ThreatIntelligenceIndicatorMetricsOperations
        threat_intelligence_indicators: ThreatIntelligenceIndicatorsOperations
        update: UpdateOperations
        watchlist_items: WatchlistItemsOperations
        watchlists: WatchlistsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.securityinsight.aio.operations

    class azure.mgmt.securityinsight.aio.operations.ActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                action_id: str, 
                action: ActionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionResponse: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                action_id: str, 
                action: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionResponse: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                action_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                action_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ActionResponse: ...

        @distributed_trace
        def list_by_alert_rule(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ActionResponse]: ...


    class azure.mgmt.securityinsight.aio.operations.AlertRuleTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                alert_rule_template_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertRuleTemplate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AlertRuleTemplate]: ...


    class azure.mgmt.securityinsight.aio.operations.AlertRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                alert_rule: AlertRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                alert_rule: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AlertRule]: ...


    class azure.mgmt.securityinsight.aio.operations.AutomationRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                automation_rule_id: str, 
                automation_rule_to_upsert: Optional[AutomationRule] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                automation_rule_id: str, 
                automation_rule_to_upsert: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                automation_rule_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                automation_rule_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AutomationRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AutomationRule]: ...


    class azure.mgmt.securityinsight.aio.operations.BookmarkOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def expand(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                parameters: BookmarkExpandParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BookmarkExpandResponse: ...

        @overload
        async def expand(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BookmarkExpandResponse: ...


    class azure.mgmt.securityinsight.aio.operations.BookmarkRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                relation: Relation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Relation: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                relation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Relation]: ...


    class azure.mgmt.securityinsight.aio.operations.BookmarksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                bookmark: Bookmark, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bookmark: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                bookmark: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bookmark: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Bookmark: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Bookmark]: ...


    class azure.mgmt.securityinsight.aio.operations.DataConnectorsCheckRequirementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connectors_check_requirements: DataConnectorsCheckRequirements, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorRequirementsState: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connectors_check_requirements: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorRequirementsState: ...


    class azure.mgmt.securityinsight.aio.operations.DataConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def connect(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                connect_body: DataConnectorConnectBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def connect(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                connect_body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                data_connector: DataConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnector: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                data_connector: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnector: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disconnect(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataConnector: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataConnector]: ...


    class azure.mgmt.securityinsight.aio.operations.DomainWhoisOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnrichmentDomainWhois: ...


    class azure.mgmt.securityinsight.aio.operations.EntitiesGetTimelineOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: EntityTimelineParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityTimelineResponse: ...

        @overload
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityTimelineResponse: ...


    class azure.mgmt.securityinsight.aio.operations.EntitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def expand(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: EntityExpandParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityExpandResponse: ...

        @overload
        async def expand(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityExpandResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Entity: ...

        @overload
        async def get_insights(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: EntityGetInsightsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityGetInsightsResponse: ...

        @overload
        async def get_insights(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityGetInsightsResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Entity]: ...

        @distributed_trace_async
        async def queries(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                kind: Union[str, EntityItemQueryKind], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GetQueriesResponse: ...


    class azure.mgmt.securityinsight.aio.operations.EntitiesRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Relation]: ...


    class azure.mgmt.securityinsight.aio.operations.EntityQueriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                entity_query: CustomEntityQuery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityQuery: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                entity_query: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityQuery: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EntityQuery: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kind: Optional[Union[str, Enum13]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[EntityQuery]: ...


    class azure.mgmt.securityinsight.aio.operations.EntityQueryTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_template_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EntityQueryTemplate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kind: Optional[Union[str, Enum15]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[EntityQueryTemplate]: ...


    class azure.mgmt.securityinsight.aio.operations.EntityRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_relation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                relation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Relation: ...


    class azure.mgmt.securityinsight.aio.operations.FileImportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FileImport]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
                file_import: FileImport, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileImport: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
                file_import: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileImport: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> FileImport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[FileImport]: ...


    class azure.mgmt.securityinsight.aio.operations.GetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def single_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Recommendation: ...


    class azure.mgmt.securityinsight.aio.operations.GetRecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RecommendationList: ...


    class azure.mgmt.securityinsight.aio.operations.IPGeodataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ip_address: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnrichmentIpGeodata: ...


    class azure.mgmt.securityinsight.aio.operations.IncidentCommentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_comment_id: str, 
                incident_comment: IncidentComment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IncidentComment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_comment_id: str, 
                incident_comment: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IncidentComment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_comment_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_comment_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IncidentComment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IncidentComment]: ...


    class azure.mgmt.securityinsight.aio.operations.IncidentRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                relation_name: str, 
                relation: Relation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Relation: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                relation_name: str, 
                relation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                relation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                relation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Relation]: ...


    class azure.mgmt.securityinsight.aio.operations.IncidentTasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_task_id: str, 
                incident_task: IncidentTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IncidentTask: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_task_id: str, 
                incident_task: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IncidentTask: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_task_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_task_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IncidentTask: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IncidentTask]: ...


    class azure.mgmt.securityinsight.aio.operations.IncidentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident: Incident, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Incident: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Incident: ...

        @overload
        async def create_team(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                team_properties: TeamInformation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TeamInformation: ...

        @overload
        async def create_team(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                team_properties: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TeamInformation: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Incident: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Incident]: ...

        @distributed_trace_async
        async def list_alerts(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IncidentAlertList: ...

        @distributed_trace_async
        async def list_bookmarks(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IncidentBookmarkList: ...

        @distributed_trace_async
        async def list_entities(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IncidentEntitiesResponse: ...

        @overload
        async def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_identifier: str, 
                request_body: Optional[ManualTriggerRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_identifier: str, 
                request_body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.securityinsight.aio.operations.MetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                metadata: MetadataModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataModel: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                metadata: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataModel: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MetadataModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[MetadataModel]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                metadata_patch: MetadataPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataModel: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                metadata_patch: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataModel: ...


    class azure.mgmt.securityinsight.aio.operations.OfficeConsentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                consent_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                consent_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OfficeConsent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[OfficeConsent]: ...


    class azure.mgmt.securityinsight.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Operation]: ...


    class azure.mgmt.securityinsight.aio.operations.ProductSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Settings: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SettingList: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                settings: Settings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                settings: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...


    class azure.mgmt.securityinsight.aio.operations.SecurityMLAnalyticsSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_resource_name: str, 
                security_ml_analytics_setting: SecurityMLAnalyticsSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityMLAnalyticsSetting: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_resource_name: str, 
                security_ml_analytics_setting: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityMLAnalyticsSetting: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SecurityMLAnalyticsSetting: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SecurityMLAnalyticsSetting]: ...


    class azure.mgmt.securityinsight.aio.operations.SentinelOnboardingStatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sentinel_onboarding_state_name: str, 
                sentinel_onboarding_state_parameter: Optional[SentinelOnboardingState] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SentinelOnboardingState: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sentinel_onboarding_state_name: str, 
                sentinel_onboarding_state_parameter: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SentinelOnboardingState: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sentinel_onboarding_state_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sentinel_onboarding_state_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SentinelOnboardingState: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SentinelOnboardingStatesList: ...


    class azure.mgmt.securityinsight.aio.operations.SourceControlOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_repositories(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                repo_type: Union[str, RepoType], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Repo]: ...


    class azure.mgmt.securityinsight.aio.operations.SourceControlsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                source_control: SourceControl, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                source_control: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SourceControl]: ...


    class azure.mgmt.securityinsight.aio.operations.ThreatIntelligenceIndicatorMetricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ThreatIntelligenceMetricsList: ...


    class azure.mgmt.securityinsight.aio.operations.ThreatIntelligenceIndicatorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def append_tags(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_append_tags: ThreatIntelligenceAppendTags, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def append_tags(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_append_tags: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_properties: ThreatIntelligenceIndicatorModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_properties: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @overload
        async def create_indicator(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_properties: ThreatIntelligenceIndicatorModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @overload
        async def create_indicator(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_properties: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @overload
        def query_indicators(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_filtering_criteria: ThreatIntelligenceFilteringCriteria, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[ThreatIntelligenceInformation]: ...

        @overload
        def query_indicators(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_filtering_criteria: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[ThreatIntelligenceInformation]: ...

        @overload
        async def replace_tags(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_replace_tags: ThreatIntelligenceIndicatorModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @overload
        async def replace_tags(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_replace_tags: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...


    class azure.mgmt.securityinsight.aio.operations.ThreatIntelligenceIndicatorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ThreatIntelligenceInformation]: ...


    class azure.mgmt.securityinsight.aio.operations.UpdateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                recommendation_patch: List[RecommendationPatch], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Recommendation]: ...

        @overload
        async def begin_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                recommendation_patch: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Recommendation]: ...


    class azure.mgmt.securityinsight.aio.operations.WatchlistItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist_item_id: str, 
                watchlist_item: WatchlistItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WatchlistItem: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist_item_id: str, 
                watchlist_item: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WatchlistItem: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist_item_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist_item_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WatchlistItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WatchlistItem]: ...


    class azure.mgmt.securityinsight.aio.operations.WatchlistsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist: Watchlist, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watchlist: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watchlist: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Watchlist: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Watchlist]: ...


namespace azure.mgmt.securityinsight.models

    class azure.mgmt.securityinsight.models.AADCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AADCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AADDataConnector(DataConnector):
        data_types: AlertsDataTypeOfDataConnector
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AADDataConnectorProperties(DataConnectorTenantId, DataConnectorWithAlertsProperties):
        data_types: AlertsDataTypeOfDataConnector
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AATPCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AATPCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AATPDataConnector(DataConnector):
        data_types: AlertsDataTypeOfDataConnector
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AATPDataConnectorProperties(DataConnectorTenantId, DataConnectorWithAlertsProperties):
        data_types: AlertsDataTypeOfDataConnector
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ASCCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        subscription_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                subscription_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ASCDataConnector(DataConnector):
        data_types: AlertsDataTypeOfDataConnector
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                etag: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ASCDataConnectorProperties(DataConnectorWithAlertsProperties):
        data_types: AlertsDataTypeOfDataConnector
        subscription_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                subscription_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AccountEntity(Entity):
        aad_tenant_id: str
        aad_user_id: str
        account_name: str
        additional_data: dict[str, any]
        display_name: str
        dns_domain: str
        friendly_name: str
        host_entity_id: str
        id: str
        is_domain_joined: bool
        kind: Union[str, EntityKind]
        name: str
        nt_domain: str
        object_guid: str
        puid: str
        sid: str
        system_data: SystemData
        type: str
        upn_suffix: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AccountEntityProperties(EntityCommonProperties):
        aad_tenant_id: str
        aad_user_id: str
        account_name: str
        additional_data: dict[str, any]
        display_name: str
        dns_domain: str
        friendly_name: str
        host_entity_id: str
        is_domain_joined: bool
        nt_domain: str
        object_guid: str
        puid: str
        sid: str
        upn_suffix: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActionPropertiesBase(Model):
        logic_app_resource_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                logic_app_resource_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActionRequest(ResourceWithEtag):
        etag: str
        id: str
        logic_app_resource_id: str
        name: str
        system_data: SystemData
        trigger_uri: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                logic_app_resource_id: Optional[str] = ..., 
                trigger_uri: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActionRequestProperties(ActionPropertiesBase):
        logic_app_resource_id: str
        trigger_uri: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                logic_app_resource_id: str, 
                trigger_uri: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActionResponse(ResourceWithEtag):
        etag: str
        id: str
        logic_app_resource_id: str
        name: str
        system_data: SystemData
        type: str
        workflow_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                logic_app_resource_id: Optional[str] = ..., 
                workflow_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActionResponseProperties(ActionPropertiesBase):
        logic_app_resource_id: str
        workflow_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                logic_app_resource_id: str, 
                workflow_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_INCIDENT_TASK = "AddIncidentTask"
        MODIFY_PROPERTIES = "ModifyProperties"
        RUN_PLAYBOOK = "RunPlaybook"


    class azure.mgmt.securityinsight.models.ActionsList(Model):
        next_link: str
        value: list[ActionResponse]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[ActionResponse], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActivityCustomEntityQuery(CustomEntityQuery):
        content: str
        created_time_utc: datetime
        description: str
        enabled: bool
        entities_filter: dict[str, list[str]]
        etag: str
        id: str
        input_entity_type: Union[str, EntityType]
        kind: Union[str, CustomEntityQueryKind]
        last_modified_time_utc: datetime
        name: str
        query_definitions: ActivityEntityQueriesPropertiesQueryDefinitions
        required_input_fields_sets: list[list[str]]
        system_data: SystemData
        template_name: str
        title: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                entities_filter: Optional[Dict[str, List[str]]] = ..., 
                etag: Optional[str] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                query_definitions: Optional[ActivityEntityQueriesPropertiesQueryDefinitions] = ..., 
                required_input_fields_sets: Optional[List[List[str]]] = ..., 
                template_name: Optional[str] = ..., 
                title: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActivityEntityQueriesPropertiesQueryDefinitions(Model):
        query: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                query: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActivityEntityQuery(EntityQuery):
        content: str
        created_time_utc: datetime
        description: str
        enabled: bool
        entities_filter: dict[str, list[str]]
        etag: str
        id: str
        input_entity_type: Union[str, EntityType]
        kind: Union[str, EntityQueryKind]
        last_modified_time_utc: datetime
        name: str
        query_definitions: ActivityEntityQueriesPropertiesQueryDefinitions
        required_input_fields_sets: list[list[str]]
        system_data: SystemData
        template_name: str
        title: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                entities_filter: Optional[Dict[str, List[str]]] = ..., 
                etag: Optional[str] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                query_definitions: Optional[ActivityEntityQueriesPropertiesQueryDefinitions] = ..., 
                required_input_fields_sets: Optional[List[List[str]]] = ..., 
                template_name: Optional[str] = ..., 
                title: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActivityEntityQueryTemplate(EntityQueryTemplate):
        content: str
        data_types: list[DataTypeDefinitions]
        description: str
        entities_filter: dict[str, list[str]]
        id: str
        input_entity_type: Union[str, EntityType]
        kind: Union[str, EntityQueryTemplateKind]
        name: str
        query_definitions: ActivityEntityQueryTemplatePropertiesQueryDefinitions
        required_input_fields_sets: list[list[str]]
        system_data: SystemData
        title: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                data_types: Optional[List[DataTypeDefinitions]] = ..., 
                description: Optional[str] = ..., 
                entities_filter: Optional[Dict[str, List[str]]] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                query_definitions: Optional[ActivityEntityQueryTemplatePropertiesQueryDefinitions] = ..., 
                required_input_fields_sets: Optional[List[List[str]]] = ..., 
                title: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActivityEntityQueryTemplatePropertiesQueryDefinitions(Model):
        query: str
        summarize_by: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                query: Optional[str] = ..., 
                summarize_by: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ActivityTimelineItem(EntityTimelineItem):
        bucket_end_time_utc: datetime
        bucket_start_time_utc: datetime
        content: str
        first_activity_time_utc: datetime
        kind: Union[str, EntityTimelineKind]
        last_activity_time_utc: datetime
        query_id: str
        title: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                bucket_end_time_utc: datetime, 
                bucket_start_time_utc: datetime, 
                content: str, 
                first_activity_time_utc: datetime, 
                last_activity_time_utc: datetime, 
                query_id: str, 
                title: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AddIncidentTaskActionProperties(Model):
        description: str
        title: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                title: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AlertDetail(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISPLAY_NAME = "DisplayName"
        SEVERITY = "Severity"


    class azure.mgmt.securityinsight.models.AlertDetailsOverride(Model):
        alert_description_format: str
        alert_display_name_format: str
        alert_dynamic_properties: list[AlertPropertyMapping]
        alert_severity_column_name: str
        alert_tactics_column_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_description_format: Optional[str] = ..., 
                alert_display_name_format: Optional[str] = ..., 
                alert_dynamic_properties: Optional[List[AlertPropertyMapping]] = ..., 
                alert_severity_column_name: Optional[str] = ..., 
                alert_tactics_column_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AlertProperty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_LINK = "AlertLink"
        CONFIDENCE_LEVEL = "ConfidenceLevel"
        CONFIDENCE_SCORE = "ConfidenceScore"
        EXTENDED_LINKS = "ExtendedLinks"
        PRODUCT_COMPONENT_NAME = "ProductComponentName"
        PRODUCT_NAME = "ProductName"
        PROVIDER_NAME = "ProviderName"
        REMEDIATION_STEPS = "RemediationSteps"
        TECHNIQUES = "Techniques"


    class azure.mgmt.securityinsight.models.AlertPropertyMapping(Model):
        alert_property: Union[str, AlertProperty]
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_property: Optional[Union[str, AlertProperty]] = ..., 
                value: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AlertRule(ResourceWithEtag):
        etag: str
        id: str
        kind: Union[str, AlertRuleKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AlertRuleKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUSION = "Fusion"
        MICROSOFT_SECURITY_INCIDENT_CREATION = "MicrosoftSecurityIncidentCreation"
        ML_BEHAVIOR_ANALYTICS = "MLBehaviorAnalytics"
        NRT = "NRT"
        SCHEDULED = "Scheduled"
        THREAT_INTELLIGENCE = "ThreatIntelligence"


    class azure.mgmt.securityinsight.models.AlertRuleTemplate(Resource):
        id: str
        kind: Union[str, AlertRuleKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AlertRuleTemplateDataSource(Model):
        connector_id: str
        data_types: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                connector_id: Optional[str] = ..., 
                data_types: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AlertRuleTemplatePropertiesBase(Model):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        last_updated_date_utc: datetime
        required_data_connectors: list[AlertRuleTemplateDataSource]
        status: Union[str, TemplateStatus]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AlertRuleTemplateWithMitreProperties(AlertRuleTemplatePropertiesBase):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        last_updated_date_utc: datetime
        required_data_connectors: list[AlertRuleTemplateDataSource]
        status: Union[str, TemplateStatus]
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AlertRuleTemplatesList(Model):
        next_link: str
        value: list[AlertRuleTemplate]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[AlertRuleTemplate], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AlertRulesList(Model):
        next_link: str
        value: list[AlertRule]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[AlertRule], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AlertSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        INFORMATIONAL = "Informational"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.securityinsight.models.AlertStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISMISSED = "Dismissed"
        IN_PROGRESS = "InProgress"
        NEW = "New"
        RESOLVED = "Resolved"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.AlertsDataTypeOfDataConnector(Model):
        alerts: DataConnectorDataTypeCommon

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alerts: DataConnectorDataTypeCommon, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Anomalies(Settings):
        etag: str
        id: str
        is_enabled: bool
        kind: Union[str, SettingKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AnomalySecurityMLAnalyticsSettings(SecurityMLAnalyticsSetting):
        anomaly_settings_version: int
        anomaly_version: str
        customizable_observations: JSON
        description: str
        display_name: str
        enabled: bool
        etag: str
        frequency: timedelta
        id: str
        is_default_settings: bool
        kind: Union[str, SecurityMLAnalyticsSettingsKind]
        last_modified_utc: datetime
        name: str
        required_data_connectors: list[SecurityMLAnalyticsSettingsDataSource]
        settings_definition_id: str
        settings_status: Union[str, SettingsStatus]
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                anomaly_settings_version: Optional[int] = ..., 
                anomaly_version: Optional[str] = ..., 
                customizable_observations: Optional[JSON] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                etag: Optional[str] = ..., 
                frequency: Optional[timedelta] = ..., 
                is_default_settings: Optional[bool] = ..., 
                required_data_connectors: Optional[List[SecurityMLAnalyticsSettingsDataSource]] = ..., 
                settings_definition_id: Optional[str] = ..., 
                settings_status: Optional[Union[str, SettingsStatus]] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AnomalyTimelineItem(EntityTimelineItem):
        azure_resource_id: str
        description: str
        display_name: str
        end_time_utc: datetime
        intent: str
        kind: Union[str, EntityTimelineKind]
        product_name: str
        reasons: list[str]
        start_time_utc: datetime
        techniques: list[str]
        time_generated: datetime
        vendor: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                azure_resource_id: str, 
                description: Optional[str] = ..., 
                display_name: str, 
                end_time_utc: datetime, 
                intent: Optional[str] = ..., 
                product_name: Optional[str] = ..., 
                reasons: Optional[List[str]] = ..., 
                start_time_utc: datetime, 
                techniques: Optional[List[str]] = ..., 
                time_generated: datetime, 
                vendor: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AntispamMailDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        INTRAORG = "Intraorg"
        OUTBOUND = "Outbound"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.AttackTactic(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLECTION = "Collection"
        COMMAND_AND_CONTROL = "CommandAndControl"
        CREDENTIAL_ACCESS = "CredentialAccess"
        DEFENSE_EVASION = "DefenseEvasion"
        DISCOVERY = "Discovery"
        EXECUTION = "Execution"
        EXFILTRATION = "Exfiltration"
        IMPACT = "Impact"
        IMPAIR_PROCESS_CONTROL = "ImpairProcessControl"
        INHIBIT_RESPONSE_FUNCTION = "InhibitResponseFunction"
        INITIAL_ACCESS = "InitialAccess"
        LATERAL_MOVEMENT = "LateralMovement"
        PERSISTENCE = "Persistence"
        PRE_ATTACK = "PreAttack"
        PRIVILEGE_ESCALATION = "PrivilegeEscalation"
        RECONNAISSANCE = "Reconnaissance"
        RESOURCE_DEVELOPMENT = "ResourceDevelopment"


    class azure.mgmt.securityinsight.models.AutomationRule(ResourceWithEtag):
        actions: list[AutomationRuleAction]
        created_by: ClientInfo
        created_time_utc: datetime
        display_name: str
        etag: str
        id: str
        last_modified_by: ClientInfo
        last_modified_time_utc: datetime
        name: str
        order: int
        system_data: SystemData
        triggering_logic: AutomationRuleTriggeringLogic
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                actions: List[AutomationRuleAction], 
                display_name: str, 
                etag: Optional[str] = ..., 
                order: int, 
                triggering_logic: AutomationRuleTriggeringLogic, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRuleAction(Model):
        action_type: Union[str, ActionType]
        order: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                order: int, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRuleAddIncidentTaskAction(AutomationRuleAction):
        action_configuration: AddIncidentTaskActionProperties
        action_type: Union[str, ActionType]
        order: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                action_configuration: Optional[AddIncidentTaskActionProperties] = ..., 
                order: int, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRuleBooleanCondition(Model):
        inner_conditions: list[AutomationRuleCondition]
        operator: Union[str, AutomationRuleBooleanConditionSupportedOperator]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                inner_conditions: Optional[List[AutomationRuleCondition]] = ..., 
                operator: Optional[Union[str, AutomationRuleBooleanConditionSupportedOperator]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRuleBooleanConditionSupportedOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AND = "And"
        OR = "Or"


    class azure.mgmt.securityinsight.models.AutomationRuleCondition(Model):
        condition_type: Union[str, ConditionType]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRuleModifyPropertiesAction(AutomationRuleAction):
        action_configuration: IncidentPropertiesAction
        action_type: Union[str, ActionType]
        order: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                action_configuration: Optional[IncidentPropertiesAction] = ..., 
                order: int, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayChangedConditionSupportedArrayType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"
        COMMENTS = "Comments"
        LABELS = "Labels"
        TACTICS = "Tactics"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayChangedConditionSupportedChangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDED = "Added"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayChangedValuesCondition(Model):
        array_type: Union[str, AutomationRulePropertyArrayChangedConditionSupportedArrayType]
        change_type: Union[str, AutomationRulePropertyArrayChangedConditionSupportedChangeType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                array_type: Optional[Union[str, AutomationRulePropertyArrayChangedConditionSupportedArrayType]] = ..., 
                change_type: Optional[Union[str, AutomationRulePropertyArrayChangedConditionSupportedChangeType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayConditionSupportedArrayConditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY_ITEM = "AnyItem"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayConditionSupportedArrayType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_DETAILS = "CustomDetails"
        CUSTOM_DETAIL_VALUES = "CustomDetailValues"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayValuesCondition(Model):
        array_condition_type: Union[str, AutomationRulePropertyArrayConditionSupportedArrayConditionType]
        array_type: Union[str, AutomationRulePropertyArrayConditionSupportedArrayType]
        item_conditions: list[AutomationRuleCondition]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                array_condition_type: Optional[Union[str, AutomationRulePropertyArrayConditionSupportedArrayConditionType]] = ..., 
                array_type: Optional[Union[str, AutomationRulePropertyArrayConditionSupportedArrayType]] = ..., 
                item_conditions: Optional[List[AutomationRuleCondition]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRulePropertyChangedConditionSupportedChangedType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANGED_FROM = "ChangedFrom"
        CHANGED_TO = "ChangedTo"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyChangedConditionSupportedPropertyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INCIDENT_OWNER = "IncidentOwner"
        INCIDENT_SEVERITY = "IncidentSeverity"
        INCIDENT_STATUS = "IncidentStatus"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyConditionSupportedOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUALS = "Equals"
        NOT_CONTAINS = "NotContains"
        NOT_ENDS_WITH = "NotEndsWith"
        NOT_EQUALS = "NotEquals"
        NOT_STARTS_WITH = "NotStartsWith"
        STARTS_WITH = "StartsWith"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyConditionSupportedProperty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_AAD_TENANT_ID = "AccountAadTenantId"
        ACCOUNT_AAD_USER_ID = "AccountAadUserId"
        ACCOUNT_NAME = "AccountName"
        ACCOUNT_NT_DOMAIN = "AccountNTDomain"
        ACCOUNT_OBJECT_GUID = "AccountObjectGuid"
        ACCOUNT_PUID = "AccountPUID"
        ACCOUNT_SID = "AccountSid"
        ACCOUNT_UPN_SUFFIX = "AccountUPNSuffix"
        ALERT_ANALYTIC_RULE_IDS = "AlertAnalyticRuleIds"
        ALERT_PRODUCT_NAMES = "AlertProductNames"
        AZURE_RESOURCE_RESOURCE_ID = "AzureResourceResourceId"
        AZURE_RESOURCE_SUBSCRIPTION_ID = "AzureResourceSubscriptionId"
        CLOUD_APPLICATION_APP_ID = "CloudApplicationAppId"
        CLOUD_APPLICATION_APP_NAME = "CloudApplicationAppName"
        DNS_DOMAIN_NAME = "DNSDomainName"
        FILE_DIRECTORY = "FileDirectory"
        FILE_HASH_VALUE = "FileHashValue"
        FILE_NAME = "FileName"
        HOST_AZURE_ID = "HostAzureID"
        HOST_NAME = "HostName"
        HOST_NET_BIOS_NAME = "HostNetBiosName"
        HOST_NT_DOMAIN = "HostNTDomain"
        HOST_OS_VERSION = "HostOSVersion"
        INCIDENT_CUSTOM_DETAILS_KEY = "IncidentCustomDetailsKey"
        INCIDENT_CUSTOM_DETAILS_VALUE = "IncidentCustomDetailsValue"
        INCIDENT_DESCRIPTION = "IncidentDescription"
        INCIDENT_LABEL = "IncidentLabel"
        INCIDENT_PROVIDER_NAME = "IncidentProviderName"
        INCIDENT_RELATED_ANALYTIC_RULE_IDS = "IncidentRelatedAnalyticRuleIds"
        INCIDENT_SEVERITY = "IncidentSeverity"
        INCIDENT_STATUS = "IncidentStatus"
        INCIDENT_TACTICS = "IncidentTactics"
        INCIDENT_TITLE = "IncidentTitle"
        INCIDENT_UPDATED_BY_SOURCE = "IncidentUpdatedBySource"
        IO_T_DEVICE_ID = "IoTDeviceId"
        IO_T_DEVICE_MODEL = "IoTDeviceModel"
        IO_T_DEVICE_NAME = "IoTDeviceName"
        IO_T_DEVICE_OPERATING_SYSTEM = "IoTDeviceOperatingSystem"
        IO_T_DEVICE_TYPE = "IoTDeviceType"
        IO_T_DEVICE_VENDOR = "IoTDeviceVendor"
        IP_ADDRESS = "IPAddress"
        MAILBOX_DISPLAY_NAME = "MailboxDisplayName"
        MAILBOX_PRIMARY_ADDRESS = "MailboxPrimaryAddress"
        MAILBOX_UPN = "MailboxUPN"
        MAIL_MESSAGE_DELIVERY_ACTION = "MailMessageDeliveryAction"
        MAIL_MESSAGE_DELIVERY_LOCATION = "MailMessageDeliveryLocation"
        MAIL_MESSAGE_P1_SENDER = "MailMessageP1Sender"
        MAIL_MESSAGE_P2_SENDER = "MailMessageP2Sender"
        MAIL_MESSAGE_RECIPIENT = "MailMessageRecipient"
        MAIL_MESSAGE_SENDER_IP = "MailMessageSenderIP"
        MAIL_MESSAGE_SUBJECT = "MailMessageSubject"
        MALWARE_CATEGORY = "MalwareCategory"
        MALWARE_NAME = "MalwareName"
        PROCESS_COMMAND_LINE = "ProcessCommandLine"
        PROCESS_ID = "ProcessId"
        REGISTRY_KEY = "RegistryKey"
        REGISTRY_VALUE_DATA = "RegistryValueData"
        URL = "Url"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyValuesChangedCondition(Model):
        change_type: Union[str, AutomationRulePropertyChangedConditionSupportedChangedType]
        operator: Union[str, AutomationRulePropertyConditionSupportedOperator]
        property_name: Union[str, AutomationRulePropertyChangedConditionSupportedPropertyType]
        property_values: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                change_type: Optional[Union[str, AutomationRulePropertyChangedConditionSupportedChangedType]] = ..., 
                operator: Optional[Union[str, AutomationRulePropertyConditionSupportedOperator]] = ..., 
                property_name: Optional[Union[str, AutomationRulePropertyChangedConditionSupportedPropertyType]] = ..., 
                property_values: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRulePropertyValuesCondition(Model):
        operator: Union[str, AutomationRulePropertyConditionSupportedOperator]
        property_name: Union[str, AutomationRulePropertyConditionSupportedProperty]
        property_values: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                operator: Optional[Union[str, AutomationRulePropertyConditionSupportedOperator]] = ..., 
                property_name: Optional[Union[str, AutomationRulePropertyConditionSupportedProperty]] = ..., 
                property_values: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRuleRunPlaybookAction(AutomationRuleAction):
        action_configuration: PlaybookActionProperties
        action_type: Union[str, ActionType]
        order: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                action_configuration: Optional[PlaybookActionProperties] = ..., 
                order: int, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRuleTriggeringLogic(Model):
        conditions: list[AutomationRuleCondition]
        expiration_time_utc: datetime
        is_enabled: bool
        triggers_on: Union[str, TriggersOn]
        triggers_when: Union[str, TriggersWhen]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                conditions: Optional[List[AutomationRuleCondition]] = ..., 
                expiration_time_utc: Optional[datetime] = ..., 
                is_enabled: bool, 
                triggers_on: Union[str, TriggersOn], 
                triggers_when: Union[str, TriggersWhen], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AutomationRulesList(Model):
        next_link: str
        value: list[AutomationRule]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AutomationRule]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Availability(Model):
        is_preview: bool
        status: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                is_preview: Optional[bool] = ..., 
                status: Optional[Literal[1]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AwsCloudTrailCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AwsCloudTrailDataConnector(DataConnector):
        aws_role_arn: str
        data_types: AwsCloudTrailDataConnectorDataTypes
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                aws_role_arn: Optional[str] = ..., 
                data_types: Optional[AwsCloudTrailDataConnectorDataTypes] = ..., 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AwsCloudTrailDataConnectorDataTypes(Model):
        logs: AwsCloudTrailDataConnectorDataTypesLogs

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                logs: AwsCloudTrailDataConnectorDataTypesLogs, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AwsCloudTrailDataConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AwsS3CheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AwsS3DataConnector(DataConnector):
        data_types: AwsS3DataConnectorDataTypes
        destination_table: str
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        role_arn: str
        sqs_urls: list[str]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AwsS3DataConnectorDataTypes] = ..., 
                destination_table: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                role_arn: Optional[str] = ..., 
                sqs_urls: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AwsS3DataConnectorDataTypes(Model):
        logs: AwsS3DataConnectorDataTypesLogs

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                logs: AwsS3DataConnectorDataTypesLogs, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AwsS3DataConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AzureDevOpsResourceInfo(Model):
        pipeline_id: str
        service_connection_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                pipeline_id: Optional[str] = ..., 
                service_connection_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AzureResourceEntity(Entity):
        additional_data: dict[str, any]
        friendly_name: str
        id: str
        kind: Union[str, EntityKind]
        name: str
        resource_id: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.AzureResourceEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        resource_id: str
        subscription_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Bookmark(ResourceWithEtag):
        created: datetime
        created_by: UserInfo
        display_name: str
        entity_mappings: list[BookmarkEntityMappings]
        etag: str
        event_time: datetime
        id: str
        incident_info: IncidentInfo
        labels: list[str]
        name: str
        notes: str
        query: str
        query_end_time: datetime
        query_result: str
        query_start_time: datetime
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        type: str
        updated: datetime
        updated_by: UserInfo

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                created_by: Optional[UserInfo] = ..., 
                display_name: Optional[str] = ..., 
                entity_mappings: Optional[List[BookmarkEntityMappings]] = ..., 
                etag: Optional[str] = ..., 
                event_time: Optional[datetime] = ..., 
                incident_info: Optional[IncidentInfo] = ..., 
                labels: Optional[List[str]] = ..., 
                notes: Optional[str] = ..., 
                query: Optional[str] = ..., 
                query_end_time: Optional[datetime] = ..., 
                query_result: Optional[str] = ..., 
                query_start_time: Optional[datetime] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                updated: Optional[datetime] = ..., 
                updated_by: Optional[UserInfo] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.BookmarkEntityMappings(Model):
        entity_type: str
        field_mappings: list[EntityFieldMapping]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                entity_type: Optional[str] = ..., 
                field_mappings: Optional[List[EntityFieldMapping]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.BookmarkExpandParameters(Model):
        end_time: datetime
        expansion_id: str
        start_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                expansion_id: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.BookmarkExpandResponse(Model):
        meta_data: ExpansionResultsMetadata
        value: BookmarkExpandResponseValue

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                meta_data: Optional[ExpansionResultsMetadata] = ..., 
                value: Optional[BookmarkExpandResponseValue] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.BookmarkExpandResponseValue(Model):
        edges: list[ConnectedEntity]
        entities: list[Entity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                edges: Optional[List[ConnectedEntity]] = ..., 
                entities: Optional[List[Entity]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.BookmarkList(Model):
        next_link: str
        value: list[Bookmark]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[Bookmark], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.BookmarkTimelineItem(EntityTimelineItem):
        azure_resource_id: str
        created_by: UserInfo
        display_name: str
        end_time_utc: datetime
        event_time: datetime
        kind: Union[str, EntityTimelineKind]
        labels: list[str]
        notes: str
        start_time_utc: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                azure_resource_id: str, 
                created_by: Optional[UserInfo] = ..., 
                display_name: Optional[str] = ..., 
                end_time_utc: Optional[datetime] = ..., 
                event_time: Optional[datetime] = ..., 
                labels: Optional[List[str]] = ..., 
                notes: Optional[str] = ..., 
                start_time_utc: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.BooleanConditionProperties(AutomationRuleCondition):
        condition_properties: AutomationRuleBooleanCondition
        condition_type: Union[str, ConditionType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                condition_properties: Optional[AutomationRuleBooleanCondition] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Category(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST_OPTIMIZATION = "CostOptimization"
        DEMO = "Demo"
        NEW_FEATURE = "NewFeature"
        ONBOARDING = "Onboarding"
        SOC_EFFICIENCY = "SocEfficiency"


    class azure.mgmt.securityinsight.models.ClientInfo(Model):
        email: str
        name: str
        object_id: str
        user_principal_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                name: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                user_principal_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CloudApplicationEntity(Entity):
        additional_data: dict[str, any]
        app_id: int
        app_name: str
        friendly_name: str
        id: str
        instance_name: str
        kind: Union[str, EntityKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CloudApplicationEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        app_id: int
        app_name: str
        friendly_name: str
        instance_name: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CloudErrorBody(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessApiPollingDataConnector(DataConnector):
        connector_ui_config: CodelessUiConnectorConfigProperties
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        polling_config: CodelessConnectorPollingConfigProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                connector_ui_config: Optional[CodelessUiConnectorConfigProperties] = ..., 
                etag: Optional[str] = ..., 
                polling_config: Optional[CodelessConnectorPollingConfigProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessConnectorPollingAuthProperties(Model):
        api_key_identifier: str
        api_key_name: str
        auth_type: str
        authorization_endpoint: str
        authorization_endpoint_query_parameters: JSON
        flow_name: str
        is_api_key_in_post_payload: str
        is_client_secret_in_header: bool
        redirection_endpoint: str
        scope: str
        token_endpoint: str
        token_endpoint_headers: JSON
        token_endpoint_query_parameters: JSON

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                api_key_identifier: Optional[str] = ..., 
                api_key_name: Optional[str] = ..., 
                auth_type: str, 
                authorization_endpoint: Optional[str] = ..., 
                authorization_endpoint_query_parameters: Optional[JSON] = ..., 
                flow_name: Optional[str] = ..., 
                is_api_key_in_post_payload: Optional[str] = ..., 
                is_client_secret_in_header: Optional[bool] = ..., 
                redirection_endpoint: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                token_endpoint: Optional[str] = ..., 
                token_endpoint_headers: Optional[JSON] = ..., 
                token_endpoint_query_parameters: Optional[JSON] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessConnectorPollingConfigProperties(Model):
        auth: CodelessConnectorPollingAuthProperties
        is_active: bool
        paging: CodelessConnectorPollingPagingProperties
        request: CodelessConnectorPollingRequestProperties
        response: CodelessConnectorPollingResponseProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auth: CodelessConnectorPollingAuthProperties, 
                is_active: Optional[bool] = ..., 
                paging: Optional[CodelessConnectorPollingPagingProperties] = ..., 
                request: CodelessConnectorPollingRequestProperties, 
                response: Optional[CodelessConnectorPollingResponseProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessConnectorPollingPagingProperties(Model):
        next_page_para_name: str
        next_page_token_json_path: str
        page_count_attribute_path: str
        page_size: int
        page_size_para_name: str
        page_time_stamp_attribute_path: str
        page_total_count_attribute_path: str
        paging_type: str
        search_the_latest_time_stamp_from_events_list: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_page_para_name: Optional[str] = ..., 
                next_page_token_json_path: Optional[str] = ..., 
                page_count_attribute_path: Optional[str] = ..., 
                page_size: Optional[int] = ..., 
                page_size_para_name: Optional[str] = ..., 
                page_time_stamp_attribute_path: Optional[str] = ..., 
                page_total_count_attribute_path: Optional[str] = ..., 
                paging_type: str, 
                search_the_latest_time_stamp_from_events_list: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessConnectorPollingRequestProperties(Model):
        api_endpoint: str
        end_time_attribute_name: str
        headers: JSON
        http_method: str
        query_parameters: JSON
        query_parameters_template: str
        query_time_format: str
        query_window_in_min: int
        rate_limit_qps: int
        retry_count: int
        start_time_attribute_name: str
        timeout_in_seconds: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                api_endpoint: str, 
                end_time_attribute_name: Optional[str] = ..., 
                headers: Optional[JSON] = ..., 
                http_method: str, 
                query_parameters: Optional[JSON] = ..., 
                query_parameters_template: Optional[str] = ..., 
                query_time_format: str, 
                query_window_in_min: int, 
                rate_limit_qps: Optional[int] = ..., 
                retry_count: Optional[int] = ..., 
                start_time_attribute_name: Optional[str] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessConnectorPollingResponseProperties(Model):
        events_json_paths: list[str]
        is_gzip_compressed: bool
        success_status_json_path: str
        success_status_value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                events_json_paths: List[str], 
                is_gzip_compressed: Optional[bool] = ..., 
                success_status_json_path: Optional[str] = ..., 
                success_status_value: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigProperties(Model):
        availability: Availability
        connectivity_criteria: list[CodelessUiConnectorConfigPropertiesConnectivityCriteriaItem]
        custom_image: str
        data_types: list[CodelessUiConnectorConfigPropertiesDataTypesItem]
        description_markdown: str
        graph_queries: list[CodelessUiConnectorConfigPropertiesGraphQueriesItem]
        graph_queries_table_name: str
        instruction_steps: list[CodelessUiConnectorConfigPropertiesInstructionStepsItem]
        permissions: Permissions
        publisher: str
        sample_queries: list[CodelessUiConnectorConfigPropertiesSampleQueriesItem]
        title: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                availability: Availability, 
                connectivity_criteria: List[CodelessUiConnectorConfigPropertiesConnectivityCriteriaItem], 
                custom_image: Optional[str] = ..., 
                data_types: List[CodelessUiConnectorConfigPropertiesDataTypesItem], 
                description_markdown: str, 
                graph_queries: List[CodelessUiConnectorConfigPropertiesGraphQueriesItem], 
                graph_queries_table_name: str, 
                instruction_steps: List[CodelessUiConnectorConfigPropertiesInstructionStepsItem], 
                permissions: Permissions, 
                publisher: str, 
                sample_queries: List[CodelessUiConnectorConfigPropertiesSampleQueriesItem], 
                title: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigPropertiesConnectivityCriteriaItem(ConnectivityCriteria):
        type: Union[str, ConnectivityType]
        value: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ConnectivityType]] = ..., 
                value: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigPropertiesDataTypesItem(LastDataReceivedDataType):
        last_data_received_query: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                last_data_received_query: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigPropertiesGraphQueriesItem(GraphQueries):
        base_query: str
        legend: str
        metric_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                base_query: Optional[str] = ..., 
                legend: Optional[str] = ..., 
                metric_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigPropertiesInstructionStepsItem(InstructionSteps):
        description: str
        instructions: list[InstructionStepsInstructionsItem]
        title: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                instructions: Optional[List[InstructionStepsInstructionsItem]] = ..., 
                title: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigPropertiesSampleQueriesItem(SampleQueries):
        description: str
        query: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                query: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CodelessUiDataConnector(DataConnector):
        connector_ui_config: CodelessUiConnectorConfigProperties
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                connector_ui_config: Optional[CodelessUiConnectorConfigProperties] = ..., 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ConditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "Boolean"
        PROPERTY = "Property"
        PROPERTY_ARRAY = "PropertyArray"
        PROPERTY_ARRAY_CHANGED = "PropertyArrayChanged"
        PROPERTY_CHANGED = "PropertyChanged"


    class azure.mgmt.securityinsight.models.ConfidenceLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.ConfidenceScoreStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FINAL = "Final"
        IN_PROCESS = "InProcess"
        NOT_APPLICABLE = "NotApplicable"
        NOT_FINAL = "NotFinal"


    class azure.mgmt.securityinsight.models.ConnectAuthKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        API_KEY = "APIKey"
        BASIC = "Basic"
        O_AUTH2 = "OAuth2"


    class azure.mgmt.securityinsight.models.ConnectedEntity(Model):
        additional_data: JSON
        target_entity_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_data: Optional[JSON] = ..., 
                target_entity_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ConnectivityCriteria(Model):
        type: Union[str, ConnectivityType]
        value: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ConnectivityType]] = ..., 
                value: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ConnectivityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IS_CONNECTED_QUERY = "IsConnectedQuery"


    class azure.mgmt.securityinsight.models.ConnectorInstructionModelBase(Model):
        parameters: JSON
        type: Union[str, SettingType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                parameters: Optional[JSON] = ..., 
                type: Union[str, SettingType], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Content(Model):
        description: str
        title: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: str, 
                title: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ContentPathMap(Model):
        content_type: Union[str, ContentType]
        path: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content_type: Optional[Union[str, ContentType]] = ..., 
                path: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYTIC_RULE = "AnalyticRule"
        WORKBOOK = "Workbook"


    class azure.mgmt.securityinsight.models.Context(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYTICS = "Analytics"
        INCIDENTS = "Incidents"
        NONE = "None"
        OVERVIEW = "Overview"


    class azure.mgmt.securityinsight.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.securityinsight.models.CustomEntityQuery(ResourceWithEtag):
        etag: str
        id: str
        kind: Union[str, CustomEntityQueryKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CustomEntityQueryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"


    class azure.mgmt.securityinsight.models.Customs(CustomsPermission):
        description: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.CustomsPermission(Model):
        description: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DataConnector(ResourceWithEtag):
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DataConnectorAuthorizationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.securityinsight.models.DataConnectorConnectBody(Model):
        api_key: str
        authorization_code: str
        client_id: str
        client_secret: str
        data_collection_endpoint: str
        data_collection_rule_immutable_id: str
        kind: Union[str, ConnectAuthKind]
        output_stream: str
        password: str
        request_config_user_input_values: list[JSON]
        user_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                api_key: Optional[str] = ..., 
                authorization_code: Optional[str] = ..., 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                data_collection_endpoint: Optional[str] = ..., 
                data_collection_rule_immutable_id: Optional[str] = ..., 
                kind: Optional[Union[str, ConnectAuthKind]] = ..., 
                output_stream: Optional[str] = ..., 
                password: Optional[str] = ..., 
                request_config_user_input_values: Optional[List[JSON]] = ..., 
                user_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DataConnectorDataTypeCommon(Model):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DataConnectorKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMAZON_WEB_SERVICES_CLOUD_TRAIL = "AmazonWebServicesCloudTrail"
        AMAZON_WEB_SERVICES_S3 = "AmazonWebServicesS3"
        API_POLLING = "APIPolling"
        AZURE_ACTIVE_DIRECTORY = "AzureActiveDirectory"
        AZURE_ADVANCED_THREAT_PROTECTION = "AzureAdvancedThreatProtection"
        AZURE_SECURITY_CENTER = "AzureSecurityCenter"
        DYNAMICS365 = "Dynamics365"
        GENERIC_UI = "GenericUI"
        IOT = "IOT"
        MICROSOFT_CLOUD_APP_SECURITY = "MicrosoftCloudAppSecurity"
        MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION = "MicrosoftDefenderAdvancedThreatProtection"
        MICROSOFT_THREAT_INTELLIGENCE = "MicrosoftThreatIntelligence"
        MICROSOFT_THREAT_PROTECTION = "MicrosoftThreatProtection"
        OFFICE365 = "Office365"
        OFFICE365_PROJECT = "Office365Project"
        OFFICE_ATP = "OfficeATP"
        OFFICE_IRM = "OfficeIRM"
        OFFICE_POWER_BI = "OfficePowerBI"
        THREAT_INTELLIGENCE = "ThreatIntelligence"
        THREAT_INTELLIGENCE_TAXII = "ThreatIntelligenceTaxii"


    class azure.mgmt.securityinsight.models.DataConnectorLicenseState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        UNKNOWN = "Unknown"
        VALID = "Valid"


    class azure.mgmt.securityinsight.models.DataConnectorList(Model):
        next_link: str
        value: list[DataConnector]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[DataConnector], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DataConnectorRequirementsState(Model):
        authorization_state: Union[str, DataConnectorAuthorizationState]
        license_state: Union[str, DataConnectorLicenseState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                authorization_state: Optional[Union[str, DataConnectorAuthorizationState]] = ..., 
                license_state: Optional[Union[str, DataConnectorLicenseState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DataConnectorTenantId(Model):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DataConnectorWithAlertsProperties(Model):
        data_types: AlertsDataTypeOfDataConnector

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DataConnectorsCheckRequirements(Model):
        kind: Union[str, DataConnectorKind]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DataTypeDefinitions(Model):
        data_type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_type: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DataTypeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.securityinsight.models.DeleteStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        NOT_DELETED = "NotDeleted"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.securityinsight.models.DeliveryAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCKED = "Blocked"
        DELIVERED = "Delivered"
        DELIVERED_AS_SPAM = "DeliveredAsSpam"
        REPLACED = "Replaced"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.DeliveryLocation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED_FOLDER = "DeletedFolder"
        DROPPED = "Dropped"
        EXTERNAL = "External"
        FAILED = "Failed"
        FORWARDED = "Forwarded"
        INBOX = "Inbox"
        JUNK_FOLDER = "JunkFolder"
        QUARANTINE = "Quarantine"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.Deployment(Model):
        deployment_id: str
        deployment_logs_url: str
        deployment_result: Union[str, DeploymentResult]
        deployment_state: Union[str, DeploymentState]
        deployment_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                deployment_id: Optional[str] = ..., 
                deployment_logs_url: Optional[str] = ..., 
                deployment_result: Optional[Union[str, DeploymentResult]] = ..., 
                deployment_state: Optional[Union[str, DeploymentState]] = ..., 
                deployment_time: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DeploymentFetchStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_FOUND = "NotFound"
        SUCCESS = "Success"
        UNAUTHORIZED = "Unauthorized"


    class azure.mgmt.securityinsight.models.DeploymentInfo(Model):
        deployment: Deployment
        deployment_fetch_status: Union[str, DeploymentFetchStatus]
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                deployment: Optional[Deployment] = ..., 
                deployment_fetch_status: Optional[Union[str, DeploymentFetchStatus]] = ..., 
                message: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DeploymentResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCESS = "Success"


    class azure.mgmt.securityinsight.models.DeploymentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELING = "Canceling"
        COMPLETED = "Completed"
        IN_PROGRESS = "In_Progress"
        QUEUED = "Queued"


    class azure.mgmt.securityinsight.models.DeviceImportance(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        NORMAL = "Normal"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.DnsEntity(Entity):
        additional_data: dict[str, any]
        dns_server_ip_entity_id: str
        domain_name: str
        friendly_name: str
        host_ip_address_entity_id: str
        id: str
        ip_address_entity_ids: list[str]
        kind: Union[str, EntityKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.DnsEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        dns_server_ip_entity_id: str
        domain_name: str
        friendly_name: str
        host_ip_address_entity_id: str
        ip_address_entity_ids: list[str]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Dynamics365CheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Dynamics365CheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Dynamics365DataConnector(DataConnector):
        data_types: Dynamics365DataConnectorDataTypes
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[Dynamics365DataConnectorDataTypes] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Dynamics365DataConnectorDataTypes(Model):
        dynamics365_cds_activities: Dynamics365DataConnectorDataTypesDynamics365CdsActivities

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                dynamics365_cds_activities: Dynamics365DataConnectorDataTypesDynamics365CdsActivities, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Dynamics365DataConnectorDataTypesDynamics365CdsActivities(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Dynamics365DataConnectorProperties(DataConnectorTenantId):
        data_types: Dynamics365DataConnectorDataTypes
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Dynamics365DataConnectorDataTypes, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ElevationToken(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        FULL = "Full"
        LIMITED = "Limited"


    class azure.mgmt.securityinsight.models.EnrichmentDomainWhois(Model):
        created: datetime
        domain: str
        expires: datetime
        parsed_whois: EnrichmentDomainWhoisDetails
        server: str
        updated: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                domain: Optional[str] = ..., 
                expires: Optional[datetime] = ..., 
                parsed_whois: Optional[EnrichmentDomainWhoisDetails] = ..., 
                server: Optional[str] = ..., 
                updated: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EnrichmentDomainWhoisContact(Model):
        city: str
        country: str
        email: str
        fax: str
        name: str
        org: str
        phone: str
        postal: str
        state: str
        street: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                city: Optional[str] = ..., 
                country: Optional[str] = ..., 
                email: Optional[str] = ..., 
                fax: Optional[str] = ..., 
                name: Optional[str] = ..., 
                org: Optional[str] = ..., 
                phone: Optional[str] = ..., 
                postal: Optional[str] = ..., 
                state: Optional[str] = ..., 
                street: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EnrichmentDomainWhoisContacts(Model):
        admin: EnrichmentDomainWhoisContact
        billing: EnrichmentDomainWhoisContact
        registrant: EnrichmentDomainWhoisContact
        tech: EnrichmentDomainWhoisContact

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                admin: Optional[EnrichmentDomainWhoisContact] = ..., 
                billing: Optional[EnrichmentDomainWhoisContact] = ..., 
                registrant: Optional[EnrichmentDomainWhoisContact] = ..., 
                tech: Optional[EnrichmentDomainWhoisContact] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EnrichmentDomainWhoisDetails(Model):
        contacts: EnrichmentDomainWhoisContacts
        name_servers: list[str]
        registrar: EnrichmentDomainWhoisRegistrarDetails
        statuses: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                contacts: Optional[EnrichmentDomainWhoisContacts] = ..., 
                name_servers: Optional[List[str]] = ..., 
                registrar: Optional[EnrichmentDomainWhoisRegistrarDetails] = ..., 
                statuses: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EnrichmentDomainWhoisRegistrarDetails(Model):
        abuse_contact_email: str
        abuse_contact_phone: str
        iana_id: str
        name: str
        url: str
        whois_server: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                abuse_contact_email: Optional[str] = ..., 
                abuse_contact_phone: Optional[str] = ..., 
                iana_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                url: Optional[str] = ..., 
                whois_server: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EnrichmentIpGeodata(Model):
        asn: str
        carrier: str
        city: str
        city_cf: int
        continent: str
        country: str
        country_cf: int
        ip_addr: str
        ip_routing_type: str
        latitude: str
        longitude: str
        organization: str
        organization_type: str
        region: str
        state: str
        state_cf: int
        state_code: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                asn: Optional[str] = ..., 
                carrier: Optional[str] = ..., 
                city: Optional[str] = ..., 
                city_cf: Optional[int] = ..., 
                continent: Optional[str] = ..., 
                country: Optional[str] = ..., 
                country_cf: Optional[int] = ..., 
                ip_addr: Optional[str] = ..., 
                ip_routing_type: Optional[str] = ..., 
                latitude: Optional[str] = ..., 
                longitude: Optional[str] = ..., 
                organization: Optional[str] = ..., 
                organization_type: Optional[str] = ..., 
                region: Optional[str] = ..., 
                state: Optional[str] = ..., 
                state_cf: Optional[int] = ..., 
                state_code: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Entity(Resource):
        id: str
        kind: Union[str, EntityKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityAnalytics(Settings):
        entity_providers: Union[list[str, EntityProviders]]
        etag: str
        id: str
        kind: Union[str, SettingKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                entity_providers: Optional[List[Union[str, EntityProviders]]] = ..., 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityCommonProperties(Model):
        additional_data: dict[str, any]
        friendly_name: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityEdges(Model):
        additional_data: dict[str, any]
        target_entity_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_data: Optional[Dict[str, Any]] = ..., 
                target_entity_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityExpandParameters(Model):
        end_time: datetime
        expansion_id: str
        start_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                expansion_id: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityExpandResponse(Model):
        meta_data: ExpansionResultsMetadata
        value: EntityExpandResponseValue

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                meta_data: Optional[ExpansionResultsMetadata] = ..., 
                value: Optional[EntityExpandResponseValue] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityExpandResponseValue(Model):
        edges: list[EntityEdges]
        entities: list[Entity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                edges: Optional[List[EntityEdges]] = ..., 
                entities: Optional[List[Entity]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityFieldMapping(Model):
        identifier: str
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                identifier: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityGetInsightsParameters(Model):
        add_default_extended_time_range: bool
        end_time: datetime
        insight_query_ids: list[str]
        start_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                add_default_extended_time_range: Optional[bool] = ..., 
                end_time: datetime, 
                insight_query_ids: Optional[List[str]] = ..., 
                start_time: datetime, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityGetInsightsResponse(Model):
        meta_data: GetInsightsResultsMetadata
        value: list[EntityInsightItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                meta_data: Optional[GetInsightsResultsMetadata] = ..., 
                value: Optional[List[EntityInsightItem]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityInsightItem(Model):
        chart_query_results: list[InsightsTableResult]
        query_id: str
        query_time_interval: EntityInsightItemQueryTimeInterval
        table_query_results: InsightsTableResult

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                chart_query_results: Optional[List[InsightsTableResult]] = ..., 
                query_id: Optional[str] = ..., 
                query_time_interval: Optional[EntityInsightItemQueryTimeInterval] = ..., 
                table_query_results: Optional[InsightsTableResult] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityInsightItemQueryTimeInterval(Model):
        end_time: datetime
        start_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityItemQueryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSIGHT = "Insight"


    class azure.mgmt.securityinsight.models.EntityKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT = "Account"
        AZURE_RESOURCE = "AzureResource"
        BOOKMARK = "Bookmark"
        CLOUD_APPLICATION = "CloudApplication"
        DNS_RESOLUTION = "DnsResolution"
        FILE = "File"
        FILE_HASH = "FileHash"
        HOST = "Host"
        IO_T_DEVICE = "IoTDevice"
        IP = "Ip"
        MAILBOX = "Mailbox"
        MAIL_CLUSTER = "MailCluster"
        MAIL_MESSAGE = "MailMessage"
        MALWARE = "Malware"
        NIC = "Nic"
        PROCESS = "Process"
        REGISTRY_KEY = "RegistryKey"
        REGISTRY_VALUE = "RegistryValue"
        SECURITY_ALERT = "SecurityAlert"
        SECURITY_GROUP = "SecurityGroup"
        SUBMISSION_MAIL = "SubmissionMail"
        URL = "Url"


    class azure.mgmt.securityinsight.models.EntityList(Model):
        next_link: str
        value: list[Entity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[Entity], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityMapping(Model):
        entity_type: Union[str, EntityMappingType]
        field_mappings: list[FieldMapping]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                entity_type: Optional[Union[str, EntityMappingType]] = ..., 
                field_mappings: Optional[List[FieldMapping]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityMappingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT = "Account"
        AZURE_RESOURCE = "AzureResource"
        CLOUD_APPLICATION = "CloudApplication"
        DNS = "DNS"
        FILE = "File"
        FILE_HASH = "FileHash"
        HOST = "Host"
        IP = "IP"
        MAILBOX = "Mailbox"
        MAIL_CLUSTER = "MailCluster"
        MAIL_MESSAGE = "MailMessage"
        MALWARE = "Malware"
        PROCESS = "Process"
        REGISTRY_KEY = "RegistryKey"
        REGISTRY_VALUE = "RegistryValue"
        SECURITY_GROUP = "SecurityGroup"
        SUBMISSION_MAIL = "SubmissionMail"
        URL = "URL"


    class azure.mgmt.securityinsight.models.EntityProviders(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_DIRECTORY = "ActiveDirectory"
        AZURE_ACTIVE_DIRECTORY = "AzureActiveDirectory"


    class azure.mgmt.securityinsight.models.EntityQuery(ResourceWithEtag):
        etag: str
        id: str
        kind: Union[str, EntityQueryKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityQueryItem(Model):
        id: str
        kind: Union[str, EntityQueryKind]
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityQueryItemProperties(Model):
        data_types: list[EntityQueryItemPropertiesDataTypesItem]
        entities_filter: JSON
        input_entity_type: Union[str, EntityType]
        required_input_fields_sets: list[list[str]]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[List[EntityQueryItemPropertiesDataTypesItem]] = ..., 
                entities_filter: Optional[JSON] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                required_input_fields_sets: Optional[List[List[str]]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityQueryItemPropertiesDataTypesItem(Model):
        data_type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_type: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityQueryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"
        EXPANSION = "Expansion"
        INSIGHT = "Insight"


    class azure.mgmt.securityinsight.models.EntityQueryList(Model):
        next_link: str
        value: list[EntityQuery]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[EntityQuery], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityQueryTemplate(Resource):
        id: str
        kind: Union[str, EntityQueryTemplateKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityQueryTemplateKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"


    class azure.mgmt.securityinsight.models.EntityQueryTemplateList(Model):
        next_link: str
        value: list[EntityQueryTemplate]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[EntityQueryTemplate], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityTimelineItem(Model):
        kind: Union[str, EntityTimelineKind]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityTimelineKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"
        ANOMALY = "Anomaly"
        BOOKMARK = "Bookmark"
        SECURITY_ALERT = "SecurityAlert"


    class azure.mgmt.securityinsight.models.EntityTimelineParameters(Model):
        end_time: datetime
        kinds: Union[list[str, EntityTimelineKind]]
        number_of_bucket: int
        start_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: datetime, 
                kinds: Optional[List[Union[str, EntityTimelineKind]]] = ..., 
                number_of_bucket: Optional[int] = ..., 
                start_time: datetime, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityTimelineResponse(Model):
        meta_data: TimelineResultsMetadata
        value: list[EntityTimelineItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                meta_data: Optional[TimelineResultsMetadata] = ..., 
                value: Optional[List[EntityTimelineItem]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EntityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT = "Account"
        AZURE_RESOURCE = "AzureResource"
        CLOUD_APPLICATION = "CloudApplication"
        DNS = "DNS"
        FILE = "File"
        FILE_HASH = "FileHash"
        HOST = "Host"
        HUNTING_BOOKMARK = "HuntingBookmark"
        IO_T_DEVICE = "IoTDevice"
        IP = "IP"
        MAILBOX = "Mailbox"
        MAIL_CLUSTER = "MailCluster"
        MAIL_MESSAGE = "MailMessage"
        MALWARE = "Malware"
        NIC = "Nic"
        PROCESS = "Process"
        REGISTRY_KEY = "RegistryKey"
        REGISTRY_VALUE = "RegistryValue"
        SECURITY_ALERT = "SecurityAlert"
        SECURITY_GROUP = "SecurityGroup"
        SUBMISSION_MAIL = "SubmissionMail"
        URL = "URL"


    class azure.mgmt.securityinsight.models.Enum13(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"
        EXPANSION = "Expansion"


    class azure.mgmt.securityinsight.models.Enum15(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"


    class azure.mgmt.securityinsight.models.EventGroupingAggregationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_PER_RESULT = "AlertPerResult"
        SINGLE_ALERT = "SingleAlert"


    class azure.mgmt.securityinsight.models.EventGroupingSettings(Model):
        aggregation_kind: Union[str, EventGroupingAggregationKind]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                aggregation_kind: Optional[Union[str, EventGroupingAggregationKind]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ExpansionEntityQuery(EntityQuery):
        data_sources: list[str]
        display_name: str
        etag: str
        id: str
        input_entity_type: Union[str, EntityType]
        input_fields: list[str]
        kind: Union[str, EntityQueryKind]
        name: str
        output_entity_types: Union[list[str, EntityType]]
        query_template: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_sources: Optional[List[str]] = ..., 
                display_name: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                input_fields: Optional[List[str]] = ..., 
                output_entity_types: Optional[List[Union[str, EntityType]]] = ..., 
                query_template: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ExpansionResultAggregation(Model):
        aggregation_type: str
        count: int
        display_name: str
        entity_kind: Union[str, EntityKind]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                count: int, 
                display_name: Optional[str] = ..., 
                entity_kind: Union[str, EntityKind], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ExpansionResultsMetadata(Model):
        aggregations: list[ExpansionResultAggregation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                aggregations: Optional[List[ExpansionResultAggregation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.EyesOn(Settings):
        etag: str
        id: str
        is_enabled: bool
        kind: Union[str, SettingKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FieldMapping(Model):
        column_name: str
        identifier: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                column_name: Optional[str] = ..., 
                identifier: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FileEntity(Entity):
        additional_data: dict[str, any]
        directory: str
        file_hash_entity_ids: list[str]
        file_name: str
        friendly_name: str
        host_entity_id: str
        id: str
        kind: Union[str, EntityKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FileEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        directory: str
        file_hash_entity_ids: list[str]
        file_name: str
        friendly_name: str
        host_entity_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FileFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSV = "CSV"
        JSON = "JSON"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.securityinsight.models.FileHashAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MD5 = "MD5"
        SHA1 = "SHA1"
        SHA256 = "SHA256"
        SHA256_AC = "SHA256AC"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.FileHashEntity(Entity):
        additional_data: dict[str, any]
        algorithm: Union[str, FileHashAlgorithm]
        friendly_name: str
        hash_value: str
        id: str
        kind: Union[str, EntityKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FileHashEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        algorithm: Union[str, FileHashAlgorithm]
        friendly_name: str
        hash_value: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FileImport(Resource):
        content_type: Union[str, FileImportContentType]
        created_time_utc: datetime
        error_file: FileMetadata
        errors_preview: list[ValidationError]
        files_valid_until_time_utc: datetime
        id: str
        import_file: FileMetadata
        import_valid_until_time_utc: datetime
        ingested_record_count: int
        ingestion_mode: Union[str, IngestionMode]
        name: str
        source: str
        state: Union[str, FileImportState]
        system_data: SystemData
        total_record_count: int
        type: str
        valid_record_count: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content_type: Optional[Union[str, FileImportContentType]] = ..., 
                import_file: Optional[FileMetadata] = ..., 
                ingestion_mode: Optional[Union[str, IngestionMode]] = ..., 
                source: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FileImportContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC_INDICATOR = "BasicIndicator"
        STIX_INDICATOR = "StixIndicator"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.securityinsight.models.FileImportList(Model):
        next_link: str
        value: list[FileImport]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[FileImport], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FileImportState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FATAL_ERROR = "FatalError"
        INGESTED = "Ingested"
        INGESTED_WITH_ERRORS = "IngestedWithErrors"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"
        UNSPECIFIED = "Unspecified"
        WAITING_FOR_UPLOAD = "WaitingForUpload"


    class azure.mgmt.securityinsight.models.FileMetadata(Model):
        delete_status: Union[str, DeleteStatus]
        file_content_uri: str
        file_format: Union[str, FileFormat]
        file_name: str
        file_size: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                file_format: Optional[Union[str, FileFormat]] = ..., 
                file_name: Optional[str] = ..., 
                file_size: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FusionAlertRule(AlertRule):
        alert_rule_template_name: str
        description: str
        display_name: str
        enabled: bool
        etag: str
        id: str
        kind: Union[str, AlertRuleKind]
        last_modified_utc: datetime
        name: str
        scenario_exclusion_patterns: list[FusionScenarioExclusionPattern]
        severity: Union[str, AlertSeverity]
        source_settings: list[FusionSourceSettings]
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rule_template_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                etag: Optional[str] = ..., 
                scenario_exclusion_patterns: Optional[List[FusionScenarioExclusionPattern]] = ..., 
                source_settings: Optional[List[FusionSourceSettings]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FusionAlertRuleTemplate(AlertRuleTemplate):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        id: str
        kind: Union[str, AlertRuleKind]
        last_updated_date_utc: datetime
        name: str
        required_data_connectors: list[AlertRuleTemplateDataSource]
        severity: Union[str, AlertSeverity]
        source_settings: list[FusionTemplateSourceSetting]
        status: Union[str, TemplateStatus]
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                source_settings: Optional[List[FusionTemplateSourceSetting]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FusionScenarioExclusionPattern(Model):
        date_added_in_utc: str
        exclusion_pattern: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                date_added_in_utc: str, 
                exclusion_pattern: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FusionSourceSettings(Model):
        enabled: bool
        source_name: str
        source_sub_types: list[FusionSourceSubTypeSetting]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                enabled: bool, 
                source_name: str, 
                source_sub_types: Optional[List[FusionSourceSubTypeSetting]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FusionSourceSubTypeSetting(Model):
        enabled: bool
        severity_filters: FusionSubTypeSeverityFilter
        source_sub_type_display_name: str
        source_sub_type_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                enabled: bool, 
                severity_filters: FusionSubTypeSeverityFilter, 
                source_sub_type_name: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FusionSubTypeSeverityFilter(Model):
        filters: list[FusionSubTypeSeverityFiltersItem]
        is_supported: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                filters: Optional[List[FusionSubTypeSeverityFiltersItem]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FusionSubTypeSeverityFiltersItem(Model):
        enabled: bool
        severity: Union[str, AlertSeverity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                enabled: bool, 
                severity: Union[str, AlertSeverity], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FusionTemplateSourceSetting(Model):
        source_name: str
        source_sub_types: list[FusionTemplateSourceSubType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                source_name: str, 
                source_sub_types: Optional[List[FusionTemplateSourceSubType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FusionTemplateSourceSubType(Model):
        severity_filter: FusionTemplateSubTypeSeverityFilter
        source_sub_type_display_name: str
        source_sub_type_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                severity_filter: FusionTemplateSubTypeSeverityFilter, 
                source_sub_type_name: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.FusionTemplateSubTypeSeverityFilter(Model):
        is_supported: bool
        severity_filters: Union[list[str, AlertSeverity]]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                is_supported: bool, 
                severity_filters: Optional[List[Union[str, AlertSeverity]]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.GeoLocation(Model):
        asn: int
        city: str
        country_code: str
        country_name: str
        latitude: float
        longitude: float
        state: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.GetInsightsError(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSIGHT = "Insight"


    class azure.mgmt.securityinsight.models.GetInsightsErrorKind(Model):
        error_message: str
        kind: Union[str, GetInsightsError]
        query_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error_message: str, 
                kind: Union[str, GetInsightsError], 
                query_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.GetInsightsResultsMetadata(Model):
        errors: list[GetInsightsErrorKind]
        total_count: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                errors: Optional[List[GetInsightsErrorKind]] = ..., 
                total_count: int, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.GetQueriesResponse(Model):
        value: list[EntityQueryItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[EntityQueryItem]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.GitHubResourceInfo(Model):
        app_installation_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                app_installation_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.GraphQueries(Model):
        base_query: str
        legend: str
        metric_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                base_query: Optional[str] = ..., 
                legend: Optional[str] = ..., 
                metric_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.GroupingConfiguration(Model):
        enabled: bool
        group_by_alert_details: Union[list[str, AlertDetail]]
        group_by_custom_details: list[str]
        group_by_entities: Union[list[str, EntityMappingType]]
        lookback_duration: timedelta
        matching_method: Union[str, MatchingMethod]
        reopen_closed_incident: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                enabled: bool, 
                group_by_alert_details: Optional[List[Union[str, AlertDetail]]] = ..., 
                group_by_custom_details: Optional[List[str]] = ..., 
                group_by_entities: Optional[List[Union[str, EntityMappingType]]] = ..., 
                lookback_duration: timedelta, 
                matching_method: Union[str, MatchingMethod], 
                reopen_closed_incident: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.HostEntity(Entity):
        additional_data: dict[str, any]
        azure_id: str
        dns_domain: str
        friendly_name: str
        host_name: str
        id: str
        is_domain_joined: bool
        kind: Union[str, EntityKind]
        name: str
        net_bios_name: str
        nt_domain: str
        oms_agent_id: str
        os_family: Union[str, OSFamily]
        os_version: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                os_family: Optional[Union[str, OSFamily]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.HostEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        azure_id: str
        dns_domain: str
        friendly_name: str
        host_name: str
        is_domain_joined: bool
        net_bios_name: str
        nt_domain: str
        oms_agent_id: str
        os_family: Union[str, OSFamily]
        os_version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                os_family: Optional[Union[str, OSFamily]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.HuntingBookmark(Entity):
        additional_data: dict[str, any]
        created: datetime
        created_by: UserInfo
        display_name: str
        event_time: datetime
        friendly_name: str
        id: str
        incident_info: IncidentInfo
        kind: Union[str, EntityKind]
        labels: list[str]
        name: str
        notes: str
        query: str
        query_result: str
        system_data: SystemData
        type: str
        updated: datetime
        updated_by: UserInfo

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                created_by: Optional[UserInfo] = ..., 
                display_name: Optional[str] = ..., 
                event_time: Optional[datetime] = ..., 
                incident_info: Optional[IncidentInfo] = ..., 
                labels: Optional[List[str]] = ..., 
                notes: Optional[str] = ..., 
                query: Optional[str] = ..., 
                query_result: Optional[str] = ..., 
                updated: Optional[datetime] = ..., 
                updated_by: Optional[UserInfo] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.HuntingBookmarkProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        created: datetime
        created_by: UserInfo
        display_name: str
        event_time: datetime
        friendly_name: str
        incident_info: IncidentInfo
        labels: list[str]
        notes: str
        query: str
        query_result: str
        updated: datetime
        updated_by: UserInfo

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                created_by: Optional[UserInfo] = ..., 
                display_name: str, 
                event_time: Optional[datetime] = ..., 
                incident_info: Optional[IncidentInfo] = ..., 
                labels: Optional[List[str]] = ..., 
                notes: Optional[str] = ..., 
                query: str, 
                query_result: Optional[str] = ..., 
                updated: Optional[datetime] = ..., 
                updated_by: Optional[UserInfo] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Incident(ResourceWithEtag):
        additional_data: IncidentAdditionalData
        classification: Union[str, IncidentClassification]
        classification_comment: str
        classification_reason: Union[str, IncidentClassificationReason]
        created_time_utc: datetime
        description: str
        etag: str
        first_activity_time_utc: datetime
        id: str
        incident_number: int
        incident_url: str
        labels: list[IncidentLabel]
        last_activity_time_utc: datetime
        last_modified_time_utc: datetime
        name: str
        owner: IncidentOwnerInfo
        provider_incident_id: str
        provider_name: str
        related_analytic_rule_ids: list[str]
        severity: Union[str, IncidentSeverity]
        status: Union[str, IncidentStatus]
        system_data: SystemData
        team_information: TeamInformation
        title: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                classification: Optional[Union[str, IncidentClassification]] = ..., 
                classification_comment: Optional[str] = ..., 
                classification_reason: Optional[Union[str, IncidentClassificationReason]] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                first_activity_time_utc: Optional[datetime] = ..., 
                labels: Optional[List[IncidentLabel]] = ..., 
                last_activity_time_utc: Optional[datetime] = ..., 
                owner: Optional[IncidentOwnerInfo] = ..., 
                provider_incident_id: Optional[str] = ..., 
                provider_name: Optional[str] = ..., 
                severity: Optional[Union[str, IncidentSeverity]] = ..., 
                status: Optional[Union[str, IncidentStatus]] = ..., 
                team_information: Optional[TeamInformation] = ..., 
                title: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentAdditionalData(Model):
        alert_product_names: list[str]
        alerts_count: int
        bookmarks_count: int
        comments_count: int
        provider_incident_url: str
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentAlertList(Model):
        value: list[SecurityAlert]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[SecurityAlert], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentBookmarkList(Model):
        value: list[HuntingBookmark]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[HuntingBookmark], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentClassification(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BENIGN_POSITIVE = "BenignPositive"
        FALSE_POSITIVE = "FalsePositive"
        TRUE_POSITIVE = "TruePositive"
        UNDETERMINED = "Undetermined"


    class azure.mgmt.securityinsight.models.IncidentClassificationReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INACCURATE_DATA = "InaccurateData"
        INCORRECT_ALERT_LOGIC = "IncorrectAlertLogic"
        SUSPICIOUS_ACTIVITY = "SuspiciousActivity"
        SUSPICIOUS_BUT_EXPECTED = "SuspiciousButExpected"


    class azure.mgmt.securityinsight.models.IncidentComment(ResourceWithEtag):
        author: ClientInfo
        created_time_utc: datetime
        etag: str
        id: str
        last_modified_time_utc: datetime
        message: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentCommentList(Model):
        next_link: str
        value: list[IncidentComment]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[IncidentComment], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentConfiguration(Model):
        create_incident: bool
        grouping_configuration: GroupingConfiguration

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                create_incident: bool, 
                grouping_configuration: Optional[GroupingConfiguration] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentEntitiesResponse(Model):
        entities: list[Entity]
        meta_data: list[IncidentEntitiesResultsMetadata]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                entities: Optional[List[Entity]] = ..., 
                meta_data: Optional[List[IncidentEntitiesResultsMetadata]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentEntitiesResultsMetadata(Model):
        count: int
        entity_kind: Union[str, EntityKind]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                count: int, 
                entity_kind: Union[str, EntityKind], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentInfo(Model):
        incident_id: str
        relation_name: str
        severity: Union[str, IncidentSeverity]
        title: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                incident_id: Optional[str] = ..., 
                relation_name: Optional[str] = ..., 
                severity: Optional[Union[str, IncidentSeverity]] = ..., 
                title: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentLabel(Model):
        label_name: str
        label_type: Union[str, IncidentLabelType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                label_name: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentLabelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_ASSIGNED = "AutoAssigned"
        USER = "User"


    class azure.mgmt.securityinsight.models.IncidentList(Model):
        next_link: str
        value: list[Incident]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[Incident], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentOwnerInfo(Model):
        assigned_to: str
        email: str
        object_id: str
        owner_type: Union[str, OwnerType]
        user_principal_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                assigned_to: Optional[str] = ..., 
                email: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                owner_type: Optional[Union[str, OwnerType]] = ..., 
                user_principal_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentPropertiesAction(Model):
        classification: Union[str, IncidentClassification]
        classification_comment: str
        classification_reason: Union[str, IncidentClassificationReason]
        labels: list[IncidentLabel]
        owner: IncidentOwnerInfo
        severity: Union[str, IncidentSeverity]
        status: Union[str, IncidentStatus]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                classification: Optional[Union[str, IncidentClassification]] = ..., 
                classification_comment: Optional[str] = ..., 
                classification_reason: Optional[Union[str, IncidentClassificationReason]] = ..., 
                labels: Optional[List[IncidentLabel]] = ..., 
                owner: Optional[IncidentOwnerInfo] = ..., 
                severity: Optional[Union[str, IncidentSeverity]] = ..., 
                status: Optional[Union[str, IncidentStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        INFORMATIONAL = "Informational"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.securityinsight.models.IncidentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CLOSED = "Closed"
        NEW = "New"


    class azure.mgmt.securityinsight.models.IncidentTask(ResourceWithEtag):
        created_by: ClientInfo
        created_time_utc: datetime
        description: str
        etag: str
        id: str
        last_modified_by: ClientInfo
        last_modified_time_utc: datetime
        name: str
        status: Union[str, IncidentTaskStatus]
        system_data: SystemData
        title: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_by: Optional[ClientInfo] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                last_modified_by: Optional[ClientInfo] = ..., 
                status: Union[str, IncidentTaskStatus], 
                title: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentTaskList(Model):
        next_link: str
        value: list[IncidentTask]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IncidentTask]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IncidentTaskStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        NEW = "New"


    class azure.mgmt.securityinsight.models.IngestionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INGEST_ANY_VALID_RECORDS = "IngestAnyValidRecords"
        INGEST_ONLY_IF_ALL_ARE_VALID = "IngestOnlyIfAllAreValid"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.securityinsight.models.InsightQueryItem(EntityQueryItem):
        id: str
        kind: Union[str, EntityQueryKind]
        name: str
        properties: InsightQueryItemProperties
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[InsightQueryItemProperties] = ..., 
                type: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemProperties(EntityQueryItemProperties):
        additional_query: InsightQueryItemPropertiesAdditionalQuery
        base_query: str
        chart_query: JSON
        data_types: list[EntityQueryItemPropertiesDataTypesItem]
        default_time_range: InsightQueryItemPropertiesDefaultTimeRange
        description: str
        display_name: str
        entities_filter: JSON
        input_entity_type: Union[str, EntityType]
        reference_time_range: InsightQueryItemPropertiesReferenceTimeRange
        required_input_fields_sets: list[list[str]]
        table_query: InsightQueryItemPropertiesTableQuery

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_query: Optional[InsightQueryItemPropertiesAdditionalQuery] = ..., 
                base_query: Optional[str] = ..., 
                chart_query: Optional[JSON] = ..., 
                data_types: Optional[List[EntityQueryItemPropertiesDataTypesItem]] = ..., 
                default_time_range: Optional[InsightQueryItemPropertiesDefaultTimeRange] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                entities_filter: Optional[JSON] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                reference_time_range: Optional[InsightQueryItemPropertiesReferenceTimeRange] = ..., 
                required_input_fields_sets: Optional[List[List[str]]] = ..., 
                table_query: Optional[InsightQueryItemPropertiesTableQuery] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesAdditionalQuery(Model):
        query: str
        text: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                query: Optional[str] = ..., 
                text: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesDefaultTimeRange(Model):
        after_range: str
        before_range: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                after_range: Optional[str] = ..., 
                before_range: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesReferenceTimeRange(Model):
        before_range: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                before_range: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesTableQuery(Model):
        columns_definitions: list[InsightQueryItemPropertiesTableQueryColumnsDefinitionsItem]
        queries_definitions: list[InsightQueryItemPropertiesTableQueryQueriesDefinitionsItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                columns_definitions: Optional[List[InsightQueryItemPropertiesTableQueryColumnsDefinitionsItem]] = ..., 
                queries_definitions: Optional[List[InsightQueryItemPropertiesTableQueryQueriesDefinitionsItem]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesTableQueryColumnsDefinitionsItem(Model):
        header: str
        output_type: Union[str, OutputType]
        support_deep_link: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                header: Optional[str] = ..., 
                output_type: Optional[Union[str, OutputType]] = ..., 
                support_deep_link: Optional[bool] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesTableQueryQueriesDefinitionsItem(Model):
        filter: str
        link_columns_definitions: list[InsightQueryItemPropertiesTableQueryQueriesDefinitionsPropertiesItemsItem]
        project: str
        summarize: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                link_columns_definitions: Optional[List[InsightQueryItemPropertiesTableQueryQueriesDefinitionsPropertiesItemsItem]] = ..., 
                project: Optional[str] = ..., 
                summarize: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesTableQueryQueriesDefinitionsPropertiesItemsItem(Model):
        projected_name: str
        query: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                projected_name: Optional[str] = ..., 
                query: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InsightsTableResult(Model):
        columns: list[InsightsTableResultColumnsItem]
        rows: list[list[str]]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                columns: Optional[List[InsightsTableResultColumnsItem]] = ..., 
                rows: Optional[List[List[str]]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InsightsTableResultColumnsItem(Model):
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InstructionSteps(Model):
        description: str
        instructions: list[InstructionStepsInstructionsItem]
        title: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                instructions: Optional[List[InstructionStepsInstructionsItem]] = ..., 
                title: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.InstructionStepsInstructionsItem(ConnectorInstructionModelBase):
        parameters: JSON
        type: Union[str, SettingType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                parameters: Optional[JSON] = ..., 
                type: Union[str, SettingType], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Instructions(Model):
        actions_to_be_performed: str
        how_to_perform_action_details: str
        recommendation_importance: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                actions_to_be_performed: str, 
                how_to_perform_action_details: Optional[str] = ..., 
                recommendation_importance: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IoTCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        subscription_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                subscription_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IoTDataConnector(DataConnector):
        data_types: AlertsDataTypeOfDataConnector
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        subscription_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                etag: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IoTDataConnectorProperties(DataConnectorWithAlertsProperties):
        data_types: AlertsDataTypeOfDataConnector
        subscription_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                subscription_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IoTDeviceEntity(Entity):
        additional_data: dict[str, any]
        device_id: str
        device_name: str
        device_sub_type: str
        device_type: str
        edge_id: str
        firmware_version: str
        friendly_name: str
        host_entity_id: str
        id: str
        importance: Union[str, DeviceImportance]
        iot_hub_entity_id: str
        iot_security_agent_id: str
        ip_address_entity_id: str
        is_authorized: bool
        is_programming: bool
        is_scanner: bool
        kind: Union[str, EntityKind]
        mac_address: str
        model: str
        name: str
        nic_entity_ids: list[str]
        operating_system: str
        owners: list[str]
        protocols: list[str]
        purdue_layer: str
        sensor: str
        serial_number: str
        site: str
        source: str
        system_data: SystemData
        threat_intelligence: list[ThreatIntelligence]
        type: str
        vendor: str
        zone: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                importance: Optional[Union[str, DeviceImportance]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IoTDeviceEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        device_id: str
        device_name: str
        device_sub_type: str
        device_type: str
        edge_id: str
        firmware_version: str
        friendly_name: str
        host_entity_id: str
        importance: Union[str, DeviceImportance]
        iot_hub_entity_id: str
        iot_security_agent_id: str
        ip_address_entity_id: str
        is_authorized: bool
        is_programming: bool
        is_scanner: bool
        mac_address: str
        model: str
        nic_entity_ids: list[str]
        operating_system: str
        owners: list[str]
        protocols: list[str]
        purdue_layer: str
        sensor: str
        serial_number: str
        site: str
        source: str
        threat_intelligence: list[ThreatIntelligence]
        vendor: str
        zone: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                importance: Optional[Union[str, DeviceImportance]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IpEntity(Entity):
        additional_data: dict[str, any]
        address: str
        friendly_name: str
        id: str
        kind: Union[str, EntityKind]
        location: GeoLocation
        name: str
        system_data: SystemData
        threat_intelligence: list[ThreatIntelligence]
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.IpEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        address: str
        friendly_name: str
        location: GeoLocation
        threat_intelligence: list[ThreatIntelligence]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.KillChainIntent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLECTION = "Collection"
        COMMAND_AND_CONTROL = "CommandAndControl"
        CREDENTIAL_ACCESS = "CredentialAccess"
        DEFENSE_EVASION = "DefenseEvasion"
        DISCOVERY = "Discovery"
        EXECUTION = "Execution"
        EXFILTRATION = "Exfiltration"
        EXPLOITATION = "Exploitation"
        IMPACT = "Impact"
        LATERAL_MOVEMENT = "LateralMovement"
        PERSISTENCE = "Persistence"
        PRIVILEGE_ESCALATION = "PrivilegeEscalation"
        PROBING = "Probing"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYTICS_RULE = "AnalyticsRule"
        ANALYTICS_RULE_TEMPLATE = "AnalyticsRuleTemplate"
        AUTOMATION_RULE = "AutomationRule"
        AZURE_FUNCTION = "AzureFunction"
        DATA_CONNECTOR = "DataConnector"
        DATA_TYPE = "DataType"
        HUNTING_QUERY = "HuntingQuery"
        INVESTIGATION_QUERY = "InvestigationQuery"
        LOGIC_APPS_CUSTOM_CONNECTOR = "LogicAppsCustomConnector"
        PARSER = "Parser"
        PLAYBOOK = "Playbook"
        PLAYBOOK_TEMPLATE = "PlaybookTemplate"
        SOLUTION = "Solution"
        WATCHLIST = "Watchlist"
        WATCHLIST_TEMPLATE = "WatchlistTemplate"
        WORKBOOK = "Workbook"
        WORKBOOK_TEMPLATE = "WorkbookTemplate"


    class azure.mgmt.securityinsight.models.LastDataReceivedDataType(Model):
        last_data_received_query: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                last_data_received_query: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MCASCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MCASCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MCASDataConnector(DataConnector):
        data_types: MCASDataConnectorDataTypes
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[MCASDataConnectorDataTypes] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MCASDataConnectorDataTypes(AlertsDataTypeOfDataConnector):
        alerts: DataConnectorDataTypeCommon
        discovery_logs: DataConnectorDataTypeCommon

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alerts: DataConnectorDataTypeCommon, 
                discovery_logs: Optional[DataConnectorDataTypeCommon] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MCASDataConnectorProperties(DataConnectorTenantId):
        data_types: MCASDataConnectorDataTypes
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: MCASDataConnectorDataTypes, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MDATPCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MDATPCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MDATPDataConnector(DataConnector):
        data_types: AlertsDataTypeOfDataConnector
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MDATPDataConnectorProperties(DataConnectorTenantId, DataConnectorWithAlertsProperties):
        data_types: AlertsDataTypeOfDataConnector
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MLBehaviorAnalyticsAlertRule(AlertRule):
        alert_rule_template_name: str
        description: str
        display_name: str
        enabled: bool
        etag: str
        id: str
        kind: Union[str, AlertRuleKind]
        last_modified_utc: datetime
        name: str
        severity: Union[str, AlertSeverity]
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rule_template_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MLBehaviorAnalyticsAlertRuleTemplate(AlertRuleTemplate):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        id: str
        kind: Union[str, AlertRuleKind]
        last_updated_date_utc: datetime
        name: str
        required_data_connectors: list[AlertRuleTemplateDataSource]
        severity: Union[str, AlertSeverity]
        status: Union[str, TemplateStatus]
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MLBehaviorAnalyticsAlertRuleTemplateProperties(AlertRuleTemplateWithMitreProperties):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        last_updated_date_utc: datetime
        required_data_connectors: list[AlertRuleTemplateDataSource]
        severity: Union[str, AlertSeverity]
        status: Union[str, TemplateStatus]
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                severity: Union[str, AlertSeverity], 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MSTICheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MSTICheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MSTIDataConnector(DataConnector):
        data_types: MSTIDataConnectorDataTypes
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[MSTIDataConnectorDataTypes] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MSTIDataConnectorDataTypes(Model):
        bing_safety_phishing_url: MSTIDataConnectorDataTypesBingSafetyPhishingURL
        microsoft_emerging_threat_feed: MSTIDataConnectorDataTypesMicrosoftEmergingThreatFeed

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                bing_safety_phishing_url: MSTIDataConnectorDataTypesBingSafetyPhishingURL, 
                microsoft_emerging_threat_feed: MSTIDataConnectorDataTypesMicrosoftEmergingThreatFeed, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MSTIDataConnectorDataTypesBingSafetyPhishingURL(DataConnectorDataTypeCommon):
        lookback_period: str
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                lookback_period: str, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MSTIDataConnectorDataTypesMicrosoftEmergingThreatFeed(DataConnectorDataTypeCommon):
        lookback_period: str
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                lookback_period: str, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MSTIDataConnectorProperties(DataConnectorTenantId):
        data_types: MSTIDataConnectorDataTypes
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: MSTIDataConnectorDataTypes, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MTPCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MTPDataConnector(DataConnector):
        data_types: MTPDataConnectorDataTypes
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[MTPDataConnectorDataTypes] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MTPDataConnectorDataTypes(Model):
        incidents: MTPDataConnectorDataTypesIncidents

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                incidents: MTPDataConnectorDataTypesIncidents, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MTPDataConnectorDataTypesIncidents(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MTPDataConnectorProperties(DataConnectorTenantId):
        data_types: MTPDataConnectorDataTypes
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: MTPDataConnectorDataTypes, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MailClusterEntity(Entity):
        additional_data: dict[str, any]
        cluster_group: str
        cluster_query_end_time: datetime
        cluster_query_start_time: datetime
        cluster_source_identifier: str
        cluster_source_type: str
        count_by_delivery_status: JSON
        count_by_protection_status: JSON
        count_by_threat_type: JSON
        friendly_name: str
        id: str
        is_volume_anomaly: bool
        kind: Union[str, EntityKind]
        mail_count: int
        name: str
        network_message_ids: list[str]
        query: str
        query_time: datetime
        source: str
        system_data: SystemData
        threats: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MailClusterEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        cluster_group: str
        cluster_query_end_time: datetime
        cluster_query_start_time: datetime
        cluster_source_identifier: str
        cluster_source_type: str
        count_by_delivery_status: JSON
        count_by_protection_status: JSON
        count_by_threat_type: JSON
        friendly_name: str
        is_volume_anomaly: bool
        mail_count: int
        network_message_ids: list[str]
        query: str
        query_time: datetime
        source: str
        threats: list[str]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MailMessageEntity(Entity):
        additional_data: dict[str, any]
        antispam_direction: Union[str, AntispamMailDirection]
        body_fingerprint_bin1: int
        body_fingerprint_bin2: int
        body_fingerprint_bin3: int
        body_fingerprint_bin4: int
        body_fingerprint_bin5: int
        delivery_action: Union[str, DeliveryAction]
        delivery_location: Union[str, DeliveryLocation]
        file_entity_ids: list[str]
        friendly_name: str
        id: str
        internet_message_id: str
        kind: Union[str, EntityKind]
        language: str
        name: str
        network_message_id: str
        p1_sender: str
        p1_sender_display_name: str
        p1_sender_domain: str
        p2_sender: str
        p2_sender_display_name: str
        p2_sender_domain: str
        receive_date: datetime
        recipient: str
        sender_ip: str
        subject: str
        system_data: SystemData
        threat_detection_methods: list[str]
        threats: list[str]
        type: str
        urls: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                antispam_direction: Optional[Union[str, AntispamMailDirection]] = ..., 
                body_fingerprint_bin1: Optional[int] = ..., 
                body_fingerprint_bin2: Optional[int] = ..., 
                body_fingerprint_bin3: Optional[int] = ..., 
                body_fingerprint_bin4: Optional[int] = ..., 
                body_fingerprint_bin5: Optional[int] = ..., 
                delivery_action: Optional[Union[str, DeliveryAction]] = ..., 
                delivery_location: Optional[Union[str, DeliveryLocation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MailMessageEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        antispam_direction: Union[str, AntispamMailDirection]
        body_fingerprint_bin1: int
        body_fingerprint_bin2: int
        body_fingerprint_bin3: int
        body_fingerprint_bin4: int
        body_fingerprint_bin5: int
        delivery_action: Union[str, DeliveryAction]
        delivery_location: Union[str, DeliveryLocation]
        file_entity_ids: list[str]
        friendly_name: str
        internet_message_id: str
        language: str
        network_message_id: str
        p1_sender: str
        p1_sender_display_name: str
        p1_sender_domain: str
        p2_sender: str
        p2_sender_display_name: str
        p2_sender_domain: str
        receive_date: datetime
        recipient: str
        sender_ip: str
        subject: str
        threat_detection_methods: list[str]
        threats: list[str]
        urls: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                antispam_direction: Optional[Union[str, AntispamMailDirection]] = ..., 
                body_fingerprint_bin1: Optional[int] = ..., 
                body_fingerprint_bin2: Optional[int] = ..., 
                body_fingerprint_bin3: Optional[int] = ..., 
                body_fingerprint_bin4: Optional[int] = ..., 
                body_fingerprint_bin5: Optional[int] = ..., 
                delivery_action: Optional[Union[str, DeliveryAction]] = ..., 
                delivery_location: Optional[Union[str, DeliveryLocation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MailboxEntity(Entity):
        additional_data: dict[str, any]
        display_name: str
        external_directory_object_id: str
        friendly_name: str
        id: str
        kind: Union[str, EntityKind]
        mailbox_primary_address: str
        name: str
        system_data: SystemData
        type: str
        upn: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MailboxEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        display_name: str
        external_directory_object_id: str
        friendly_name: str
        mailbox_primary_address: str
        upn: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MalwareEntity(Entity):
        additional_data: dict[str, any]
        category: str
        file_entity_ids: list[str]
        friendly_name: str
        id: str
        kind: Union[str, EntityKind]
        malware_name: str
        name: str
        process_entity_ids: list[str]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MalwareEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        category: str
        file_entity_ids: list[str]
        friendly_name: str
        malware_name: str
        process_entity_ids: list[str]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ManualTriggerRequestBody(Model):
        logic_apps_resource_id: str
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                logic_apps_resource_id: str, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MatchingMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_ENTITIES = "AllEntities"
        ANY_ALERT = "AnyAlert"
        SELECTED = "Selected"


    class azure.mgmt.securityinsight.models.MetadataAuthor(Model):
        email: str
        link: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                link: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MetadataCategories(Model):
        domains: list[str]
        verticals: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                domains: Optional[List[str]] = ..., 
                verticals: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MetadataDependencies(Model):
        content_id: str
        criteria: list[MetadataDependencies]
        kind: Union[str, Kind]
        name: str
        operator: Union[str, Operator]
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content_id: Optional[str] = ..., 
                criteria: Optional[List[MetadataDependencies]] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                name: Optional[str] = ..., 
                operator: Optional[Union[str, Operator]] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MetadataList(Model):
        next_link: str
        value: list[MetadataModel]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[MetadataModel], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MetadataModel(ResourceWithEtag):
        author: MetadataAuthor
        categories: MetadataCategories
        content_id: str
        content_schema_version: str
        custom_version: str
        dependencies: MetadataDependencies
        etag: str
        first_publish_date: date
        icon: str
        id: str
        kind: Union[str, Kind]
        last_publish_date: date
        name: str
        parent_id: str
        preview_images: list[str]
        preview_images_dark: list[str]
        providers: list[str]
        source: MetadataSource
        support: MetadataSupport
        system_data: SystemData
        threat_analysis_tactics: list[str]
        threat_analysis_techniques: list[str]
        type: str
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                author: Optional[MetadataAuthor] = ..., 
                categories: Optional[MetadataCategories] = ..., 
                content_id: Optional[str] = ..., 
                content_schema_version: Optional[str] = ..., 
                custom_version: Optional[str] = ..., 
                dependencies: Optional[MetadataDependencies] = ..., 
                etag: Optional[str] = ..., 
                first_publish_date: Optional[date] = ..., 
                icon: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                last_publish_date: Optional[date] = ..., 
                parent_id: Optional[str] = ..., 
                preview_images: Optional[List[str]] = ..., 
                preview_images_dark: Optional[List[str]] = ..., 
                providers: Optional[List[str]] = ..., 
                source: Optional[MetadataSource] = ..., 
                support: Optional[MetadataSupport] = ..., 
                threat_analysis_tactics: Optional[List[str]] = ..., 
                threat_analysis_techniques: Optional[List[str]] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MetadataPatch(ResourceWithEtag):
        author: MetadataAuthor
        categories: MetadataCategories
        content_id: str
        content_schema_version: str
        custom_version: str
        dependencies: MetadataDependencies
        etag: str
        first_publish_date: date
        icon: str
        id: str
        kind: Union[str, Kind]
        last_publish_date: date
        name: str
        parent_id: str
        preview_images: list[str]
        preview_images_dark: list[str]
        providers: list[str]
        source: MetadataSource
        support: MetadataSupport
        system_data: SystemData
        threat_analysis_tactics: list[str]
        threat_analysis_techniques: list[str]
        type: str
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                author: Optional[MetadataAuthor] = ..., 
                categories: Optional[MetadataCategories] = ..., 
                content_id: Optional[str] = ..., 
                content_schema_version: Optional[str] = ..., 
                custom_version: Optional[str] = ..., 
                dependencies: Optional[MetadataDependencies] = ..., 
                etag: Optional[str] = ..., 
                first_publish_date: Optional[date] = ..., 
                icon: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                last_publish_date: Optional[date] = ..., 
                parent_id: Optional[str] = ..., 
                preview_images: Optional[List[str]] = ..., 
                preview_images_dark: Optional[List[str]] = ..., 
                providers: Optional[List[str]] = ..., 
                source: Optional[MetadataSource] = ..., 
                support: Optional[MetadataSupport] = ..., 
                threat_analysis_tactics: Optional[List[str]] = ..., 
                threat_analysis_techniques: Optional[List[str]] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MetadataSource(Model):
        kind: Union[str, SourceKind]
        name: str
        source_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                kind: Union[str, SourceKind], 
                name: Optional[str] = ..., 
                source_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MetadataSupport(Model):
        email: str
        link: str
        name: str
        tier: Union[str, SupportTier]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                link: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tier: Union[str, SupportTier], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityIncidentCreationAlertRule(AlertRule):
        alert_rule_template_name: str
        description: str
        display_name: str
        display_names_exclude_filter: list[str]
        display_names_filter: list[str]
        enabled: bool
        etag: str
        id: str
        kind: Union[str, AlertRuleKind]
        last_modified_utc: datetime
        name: str
        product_filter: Union[str, MicrosoftSecurityProductName]
        severities_filter: Union[list[str, AlertSeverity]]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rule_template_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                display_names_exclude_filter: Optional[List[str]] = ..., 
                display_names_filter: Optional[List[str]] = ..., 
                enabled: Optional[bool] = ..., 
                etag: Optional[str] = ..., 
                product_filter: Optional[Union[str, MicrosoftSecurityProductName]] = ..., 
                severities_filter: Optional[List[Union[str, AlertSeverity]]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityIncidentCreationAlertRuleCommonProperties(Model):
        display_names_exclude_filter: list[str]
        display_names_filter: list[str]
        product_filter: Union[str, MicrosoftSecurityProductName]
        severities_filter: Union[list[str, AlertSeverity]]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display_names_exclude_filter: Optional[List[str]] = ..., 
                display_names_filter: Optional[List[str]] = ..., 
                product_filter: Union[str, MicrosoftSecurityProductName], 
                severities_filter: Optional[List[Union[str, AlertSeverity]]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityIncidentCreationAlertRuleProperties(MicrosoftSecurityIncidentCreationAlertRuleCommonProperties):
        alert_rule_template_name: str
        description: str
        display_name: str
        display_names_exclude_filter: list[str]
        display_names_filter: list[str]
        enabled: bool
        last_modified_utc: datetime
        product_filter: Union[str, MicrosoftSecurityProductName]
        severities_filter: Union[list[str, AlertSeverity]]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rule_template_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                display_names_exclude_filter: Optional[List[str]] = ..., 
                display_names_filter: Optional[List[str]] = ..., 
                enabled: bool, 
                product_filter: Union[str, MicrosoftSecurityProductName], 
                severities_filter: Optional[List[Union[str, AlertSeverity]]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityIncidentCreationAlertRuleTemplate(AlertRuleTemplate):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        display_names_exclude_filter: list[str]
        display_names_filter: list[str]
        id: str
        kind: Union[str, AlertRuleKind]
        last_updated_date_utc: datetime
        name: str
        product_filter: Union[str, MicrosoftSecurityProductName]
        required_data_connectors: list[AlertRuleTemplateDataSource]
        severities_filter: Union[list[str, AlertSeverity]]
        status: Union[str, TemplateStatus]
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                display_names_exclude_filter: Optional[List[str]] = ..., 
                display_names_filter: Optional[List[str]] = ..., 
                product_filter: Optional[Union[str, MicrosoftSecurityProductName]] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                severities_filter: Optional[List[Union[str, AlertSeverity]]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityIncidentCreationAlertRuleTemplateProperties(AlertRuleTemplatePropertiesBase):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        display_names_exclude_filter: list[str]
        display_names_filter: list[str]
        last_updated_date_utc: datetime
        product_filter: Union[str, MicrosoftSecurityProductName]
        required_data_connectors: list[AlertRuleTemplateDataSource]
        severities_filter: Union[list[str, AlertSeverity]]
        status: Union[str, TemplateStatus]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                display_names_exclude_filter: Optional[List[str]] = ..., 
                display_names_filter: Optional[List[str]] = ..., 
                product_filter: Optional[Union[str, MicrosoftSecurityProductName]] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                severities_filter: Optional[List[Union[str, AlertSeverity]]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityProductName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ACTIVE_DIRECTORY_IDENTITY_PROTECTION = "Azure Active Directory Identity Protection"
        AZURE_ADVANCED_THREAT_PROTECTION = "Azure Advanced Threat Protection"
        AZURE_SECURITY_CENTER = "Azure Security Center"
        AZURE_SECURITY_CENTER_FOR_IO_T = "Azure Security Center for IoT"
        MICROSOFT_CLOUD_APP_SECURITY = "Microsoft Cloud App Security"
        MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION = "Microsoft Defender Advanced Threat Protection"
        OFFICE365_ADVANCED_THREAT_PROTECTION = "Office 365 Advanced Threat Protection"


    class azure.mgmt.securityinsight.models.MtpCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.NicEntity(Entity):
        additional_data: dict[str, any]
        friendly_name: str
        id: str
        ip_address_entity_id: str
        kind: Union[str, EntityKind]
        mac_address: str
        name: str
        system_data: SystemData
        type: str
        vlans: list[str]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.NicEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        ip_address_entity_id: str
        mac_address: str
        vlans: list[str]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.NrtAlertRule(AlertRule):
        alert_details_override: AlertDetailsOverride
        alert_rule_template_name: str
        custom_details: dict[str, str]
        description: str
        display_name: str
        enabled: bool
        entity_mappings: list[EntityMapping]
        etag: str
        event_grouping_settings: EventGroupingSettings
        id: str
        incident_configuration: IncidentConfiguration
        kind: Union[str, AlertRuleKind]
        last_modified_utc: datetime
        name: str
        query: str
        sentinel_entities_mappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        suppression_duration: timedelta
        suppression_enabled: bool
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        template_version: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                alert_rule_template_name: Optional[str] = ..., 
                custom_details: Optional[Dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                entity_mappings: Optional[List[EntityMapping]] = ..., 
                etag: Optional[str] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                incident_configuration: Optional[IncidentConfiguration] = ..., 
                query: Optional[str] = ..., 
                sentinel_entities_mappings: Optional[List[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                suppression_duration: Optional[timedelta] = ..., 
                suppression_enabled: Optional[bool] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                template_version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.NrtAlertRuleTemplate(AlertRuleTemplate):
        alert_details_override: AlertDetailsOverride
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        custom_details: dict[str, str]
        description: str
        display_name: str
        entity_mappings: list[EntityMapping]
        event_grouping_settings: EventGroupingSettings
        id: str
        kind: Union[str, AlertRuleKind]
        last_updated_date_utc: datetime
        name: str
        query: str
        required_data_connectors: list[AlertRuleTemplateDataSource]
        sentinel_entities_mappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        status: Union[str, TemplateStatus]
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        type: str
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                custom_details: Optional[Dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                entity_mappings: Optional[List[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                query: Optional[str] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                sentinel_entities_mappings: Optional[List[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.NrtAlertRuleTemplateProperties(AlertRuleTemplateWithMitreProperties, QueryBasedAlertRuleTemplateProperties):
        alert_details_override: AlertDetailsOverride
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        custom_details: dict[str, str]
        description: str
        display_name: str
        entity_mappings: list[EntityMapping]
        event_grouping_settings: EventGroupingSettings
        last_updated_date_utc: datetime
        query: str
        required_data_connectors: list[AlertRuleTemplateDataSource]
        sentinel_entities_mappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        status: Union[str, TemplateStatus]
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                custom_details: Optional[Dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                entity_mappings: Optional[List[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                query: Optional[str] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                sentinel_entities_mappings: Optional[List[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OSFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANDROID = "Android"
        IOS = "IOS"
        LINUX = "Linux"
        UNKNOWN = "Unknown"
        WINDOWS = "Windows"


    class azure.mgmt.securityinsight.models.Office365ProjectCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Office365ProjectCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Office365ProjectConnectorDataTypes(Model):
        logs: Office365ProjectConnectorDataTypesLogs

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                logs: Office365ProjectConnectorDataTypesLogs, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Office365ProjectConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Office365ProjectDataConnector(DataConnector):
        data_types: Office365ProjectConnectorDataTypes
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[Office365ProjectConnectorDataTypes] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Office365ProjectDataConnectorProperties(DataConnectorTenantId):
        data_types: Office365ProjectConnectorDataTypes
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Office365ProjectConnectorDataTypes, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeATPCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeATPCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeATPDataConnector(DataConnector):
        data_types: AlertsDataTypeOfDataConnector
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeATPDataConnectorProperties(DataConnectorTenantId, DataConnectorWithAlertsProperties):
        data_types: AlertsDataTypeOfDataConnector
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeConsent(Resource):
        consent_id: str
        id: str
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                consent_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeConsentList(Model):
        next_link: str
        value: list[OfficeConsent]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[OfficeConsent], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnector(DataConnector):
        data_types: OfficeDataConnectorDataTypes
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[OfficeDataConnectorDataTypes] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnectorDataTypes(Model):
        exchange: OfficeDataConnectorDataTypesExchange
        share_point: OfficeDataConnectorDataTypesSharePoint
        teams: OfficeDataConnectorDataTypesTeams

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                exchange: OfficeDataConnectorDataTypesExchange, 
                share_point: OfficeDataConnectorDataTypesSharePoint, 
                teams: OfficeDataConnectorDataTypesTeams, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnectorDataTypesExchange(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnectorDataTypesSharePoint(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnectorDataTypesTeams(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnectorProperties(DataConnectorTenantId):
        data_types: OfficeDataConnectorDataTypes
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: OfficeDataConnectorDataTypes, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeIRMCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeIRMCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeIRMDataConnector(DataConnector):
        data_types: AlertsDataTypeOfDataConnector
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficeIRMDataConnectorProperties(DataConnectorTenantId, DataConnectorWithAlertsProperties):
        data_types: AlertsDataTypeOfDataConnector
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficePowerBICheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficePowerBICheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficePowerBIConnectorDataTypes(Model):
        logs: OfficePowerBIConnectorDataTypesLogs

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                logs: OfficePowerBIConnectorDataTypesLogs, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficePowerBIConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficePowerBIDataConnector(DataConnector):
        data_types: OfficePowerBIConnectorDataTypes
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[OfficePowerBIConnectorDataTypes] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OfficePowerBIDataConnectorProperties(DataConnectorTenantId):
        data_types: OfficePowerBIConnectorDataTypes
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: OfficePowerBIConnectorDataTypes, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.OperationsList(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[Operation], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AND = "AND"
        OR = "OR"


    class azure.mgmt.securityinsight.models.OutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATE = "Date"
        ENTITY = "Entity"
        NUMBER = "Number"
        STRING = "String"


    class azure.mgmt.securityinsight.models.OwnerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "Group"
        UNKNOWN = "Unknown"
        USER = "User"


    class azure.mgmt.securityinsight.models.PermissionProviderScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESOURCE_GROUP = "ResourceGroup"
        SUBSCRIPTION = "Subscription"
        WORKSPACE = "Workspace"


    class azure.mgmt.securityinsight.models.Permissions(Model):
        customs: list[PermissionsCustomsItem]
        resource_provider: list[PermissionsResourceProviderItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                customs: Optional[List[PermissionsCustomsItem]] = ..., 
                resource_provider: Optional[List[PermissionsResourceProviderItem]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.PermissionsCustomsItem(Customs):
        description: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.PermissionsResourceProviderItem(ResourceProvider):
        permissions_display_text: str
        provider: Union[str, ProviderName]
        provider_display_name: str
        required_permissions: RequiredPermissions
        scope: Union[str, PermissionProviderScope]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                permissions_display_text: Optional[str] = ..., 
                provider: Optional[Union[str, ProviderName]] = ..., 
                provider_display_name: Optional[str] = ..., 
                required_permissions: Optional[RequiredPermissions] = ..., 
                scope: Optional[Union[str, PermissionProviderScope]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.PlaybookActionProperties(Model):
        logic_app_resource_id: str
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                logic_app_resource_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.PollingFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONCE_AN_HOUR = "OnceAnHour"
        ONCE_A_DAY = "OnceADay"
        ONCE_A_MINUTE = "OnceAMinute"


    class azure.mgmt.securityinsight.models.Priority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.securityinsight.models.ProcessEntity(Entity):
        account_entity_id: str
        additional_data: dict[str, any]
        command_line: str
        creation_time_utc: datetime
        elevation_token: Union[str, ElevationToken]
        friendly_name: str
        host_entity_id: str
        host_logon_session_entity_id: str
        id: str
        image_file_entity_id: str
        kind: Union[str, EntityKind]
        name: str
        parent_process_entity_id: str
        process_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                elevation_token: Optional[Union[str, ElevationToken]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ProcessEntityProperties(EntityCommonProperties):
        account_entity_id: str
        additional_data: dict[str, any]
        command_line: str
        creation_time_utc: datetime
        elevation_token: Union[str, ElevationToken]
        friendly_name: str
        host_entity_id: str
        host_logon_session_entity_id: str
        image_file_entity_id: str
        parent_process_entity_id: str
        process_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                elevation_token: Optional[Union[str, ElevationToken]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.PropertyArrayChangedConditionProperties(AutomationRuleCondition):
        condition_properties: AutomationRulePropertyArrayChangedValuesCondition
        condition_type: Union[str, ConditionType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                condition_properties: Optional[AutomationRulePropertyArrayChangedValuesCondition] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.PropertyArrayConditionProperties(AutomationRuleCondition):
        condition_properties: AutomationRulePropertyArrayValuesCondition
        condition_type: Union[str, ConditionType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                condition_properties: Optional[AutomationRulePropertyArrayValuesCondition] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.PropertyChangedConditionProperties(AutomationRuleCondition):
        condition_properties: AutomationRulePropertyValuesChangedCondition
        condition_type: Union[str, ConditionType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                condition_properties: Optional[AutomationRulePropertyValuesChangedCondition] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.PropertyConditionProperties(AutomationRuleCondition):
        condition_properties: AutomationRulePropertyValuesCondition
        condition_type: Union[str, ConditionType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                condition_properties: Optional[AutomationRulePropertyValuesCondition] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ProviderName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_AADIAM_DIAGNOSTIC_SETTINGS = "microsoft.aadiam/diagnosticSettings"
        MICROSOFT_AUTHORIZATION_POLICY_ASSIGNMENTS = "Microsoft.Authorization/policyAssignments"
        MICROSOFT_OPERATIONAL_INSIGHTS_SOLUTIONS = "Microsoft.OperationalInsights/solutions"
        MICROSOFT_OPERATIONAL_INSIGHTS_WORKSPACES = "Microsoft.OperationalInsights/workspaces"
        MICROSOFT_OPERATIONAL_INSIGHTS_WORKSPACES_DATASOURCES = "Microsoft.OperationalInsights/workspaces/datasources"
        MICROSOFT_OPERATIONAL_INSIGHTS_WORKSPACES_SHARED_KEYS = "Microsoft.OperationalInsights/workspaces/sharedKeys"


    class azure.mgmt.securityinsight.models.QueryBasedAlertRuleTemplateProperties(Model):
        alert_details_override: AlertDetailsOverride
        custom_details: dict[str, str]
        entity_mappings: list[EntityMapping]
        event_grouping_settings: EventGroupingSettings
        query: str
        sentinel_entities_mappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                custom_details: Optional[Dict[str, str]] = ..., 
                entity_mappings: Optional[List[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                query: Optional[str] = ..., 
                sentinel_entities_mappings: Optional[List[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Recommendation(Model):
        actions: list[RecommendedAction]
        additional_properties: dict[str, str]
        category: Union[str, Category]
        content: Content
        context: Union[str, Context]
        description: str
        display_until_time_utc: datetime
        hide_until_time_utc: datetime
        id: str
        instructions: Instructions
        last_evaluated_time_utc: datetime
        priority: Union[str, Priority]
        recommendation_type_id: str
        recommendation_type_title: str
        resource_id: str
        state: Union[str, State]
        title: str
        visible: bool
        workspace_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                actions: List[RecommendedAction], 
                additional_properties: Optional[Dict[str, str]] = ..., 
                category: Union[str, Category], 
                content: Optional[Content] = ..., 
                context: Union[str, Context], 
                description: str, 
                display_until_time_utc: Optional[datetime] = ..., 
                hide_until_time_utc: Optional[datetime] = ..., 
                id: str, 
                instructions: Instructions, 
                last_evaluated_time_utc: datetime, 
                priority: Union[str, Priority], 
                recommendation_type_id: str, 
                recommendation_type_title: str, 
                resource_id: Optional[str] = ..., 
                state: Union[str, State], 
                title: str, 
                visible: Optional[bool] = ..., 
                workspace_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RecommendationList(Model):
        value: list[Recommendation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Recommendation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RecommendationPatch(Model):
        hide_until_time_utc: datetime
        state: Union[str, State]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                hide_until_time_utc: Optional[datetime] = ..., 
                state: Optional[Union[str, State]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RecommendedAction(Model):
        link_text: str
        link_url: str
        state: Union[str, Priority]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                link_text: str, 
                link_url: str, 
                state: Optional[Union[str, Priority]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RegistryHive(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HKEY_A = "HKEY_A"
        HKEY_CLASSES_ROOT = "HKEY_CLASSES_ROOT"
        HKEY_CURRENT_CONFIG = "HKEY_CURRENT_CONFIG"
        HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
        HKEY_CURRENT_USER_LOCAL_SETTINGS = "HKEY_CURRENT_USER_LOCAL_SETTINGS"
        HKEY_LOCAL_MACHINE = "HKEY_LOCAL_MACHINE"
        HKEY_PERFORMANCE_DATA = "HKEY_PERFORMANCE_DATA"
        HKEY_PERFORMANCE_NLSTEXT = "HKEY_PERFORMANCE_NLSTEXT"
        HKEY_PERFORMANCE_TEXT = "HKEY_PERFORMANCE_TEXT"
        HKEY_USERS = "HKEY_USERS"


    class azure.mgmt.securityinsight.models.RegistryKeyEntity(Entity):
        additional_data: dict[str, any]
        friendly_name: str
        hive: Union[str, RegistryHive]
        id: str
        key: str
        kind: Union[str, EntityKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RegistryKeyEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        hive: Union[str, RegistryHive]
        key: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RegistryValueEntity(Entity):
        additional_data: dict[str, any]
        friendly_name: str
        id: str
        key_entity_id: str
        kind: Union[str, EntityKind]
        name: str
        system_data: SystemData
        type: str
        value_data: str
        value_name: str
        value_type: Union[str, RegistryValueKind]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RegistryValueEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        key_entity_id: str
        value_data: str
        value_name: str
        value_type: Union[str, RegistryValueKind]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RegistryValueKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY = "Binary"
        D_WORD = "DWord"
        EXPAND_STRING = "ExpandString"
        MULTI_STRING = "MultiString"
        NONE = "None"
        Q_WORD = "QWord"
        STRING = "String"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.Relation(ResourceWithEtag):
        etag: str
        id: str
        name: str
        related_resource_id: str
        related_resource_kind: str
        related_resource_name: str
        related_resource_type: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                related_resource_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RelationList(Model):
        next_link: str
        value: list[Relation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[Relation], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Repo(Model):
        branches: list[str]
        full_name: str
        url: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                branches: Optional[List[str]] = ..., 
                full_name: Optional[str] = ..., 
                url: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RepoList(Model):
        next_link: str
        value: list[Repo]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[Repo], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RepoType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEV_OPS = "DevOps"
        GITHUB = "Github"


    class azure.mgmt.securityinsight.models.Repository(Model):
        branch: str
        deployment_logs_url: str
        display_url: str
        path_mapping: list[ContentPathMap]
        url: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                branch: Optional[str] = ..., 
                deployment_logs_url: Optional[str] = ..., 
                display_url: Optional[str] = ..., 
                path_mapping: Optional[List[ContentPathMap]] = ..., 
                url: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RepositoryResourceInfo(Model):
        azure_dev_ops_resource_info: AzureDevOpsResourceInfo
        git_hub_resource_info: GitHubResourceInfo
        webhook: Webhook

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                azure_dev_ops_resource_info: Optional[AzureDevOpsResourceInfo] = ..., 
                git_hub_resource_info: Optional[GitHubResourceInfo] = ..., 
                webhook: Optional[Webhook] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.RequiredPermissions(Model):
        action: bool
        delete: bool
        read: bool
        write: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                action: Optional[bool] = ..., 
                delete: Optional[bool] = ..., 
                read: Optional[bool] = ..., 
                write: Optional[bool] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ResourceProvider(Model):
        permissions_display_text: str
        provider: Union[str, ProviderName]
        provider_display_name: str
        required_permissions: RequiredPermissions
        scope: Union[str, PermissionProviderScope]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                permissions_display_text: Optional[str] = ..., 
                provider: Optional[Union[str, ProviderName]] = ..., 
                provider_display_name: Optional[str] = ..., 
                required_permissions: Optional[RequiredPermissions] = ..., 
                scope: Optional[Union[str, PermissionProviderScope]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ResourceWithEtag(Resource):
        etag: str
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SampleQueries(Model):
        description: str
        query: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                query: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ScheduledAlertRule(AlertRule):
        alert_details_override: AlertDetailsOverride
        alert_rule_template_name: str
        custom_details: dict[str, str]
        description: str
        display_name: str
        enabled: bool
        entity_mappings: list[EntityMapping]
        etag: str
        event_grouping_settings: EventGroupingSettings
        id: str
        incident_configuration: IncidentConfiguration
        kind: Union[str, AlertRuleKind]
        last_modified_utc: datetime
        name: str
        query: str
        query_frequency: timedelta
        query_period: timedelta
        sentinel_entities_mappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        suppression_duration: timedelta
        suppression_enabled: bool
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        template_version: str
        trigger_operator: Union[str, TriggerOperator]
        trigger_threshold: int
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                alert_rule_template_name: Optional[str] = ..., 
                custom_details: Optional[Dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                entity_mappings: Optional[List[EntityMapping]] = ..., 
                etag: Optional[str] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                incident_configuration: Optional[IncidentConfiguration] = ..., 
                query: Optional[str] = ..., 
                query_frequency: Optional[timedelta] = ..., 
                query_period: Optional[timedelta] = ..., 
                sentinel_entities_mappings: Optional[List[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                suppression_duration: Optional[timedelta] = ..., 
                suppression_enabled: Optional[bool] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                template_version: Optional[str] = ..., 
                trigger_operator: Optional[Union[str, TriggerOperator]] = ..., 
                trigger_threshold: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ScheduledAlertRuleCommonProperties(Model):
        alert_details_override: AlertDetailsOverride
        custom_details: dict[str, str]
        entity_mappings: list[EntityMapping]
        event_grouping_settings: EventGroupingSettings
        query: str
        query_frequency: timedelta
        query_period: timedelta
        sentinel_entities_mappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        trigger_operator: Union[str, TriggerOperator]
        trigger_threshold: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                custom_details: Optional[Dict[str, str]] = ..., 
                entity_mappings: Optional[List[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                query: Optional[str] = ..., 
                query_frequency: Optional[timedelta] = ..., 
                query_period: Optional[timedelta] = ..., 
                sentinel_entities_mappings: Optional[List[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                trigger_operator: Optional[Union[str, TriggerOperator]] = ..., 
                trigger_threshold: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ScheduledAlertRuleProperties(ScheduledAlertRuleCommonProperties):
        alert_details_override: AlertDetailsOverride
        alert_rule_template_name: str
        custom_details: dict[str, str]
        description: str
        display_name: str
        enabled: bool
        entity_mappings: list[EntityMapping]
        event_grouping_settings: EventGroupingSettings
        incident_configuration: IncidentConfiguration
        last_modified_utc: datetime
        query: str
        query_frequency: timedelta
        query_period: timedelta
        sentinel_entities_mappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        suppression_duration: timedelta
        suppression_enabled: bool
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        template_version: str
        trigger_operator: Union[str, TriggerOperator]
        trigger_threshold: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                alert_rule_template_name: Optional[str] = ..., 
                custom_details: Optional[Dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                enabled: bool, 
                entity_mappings: Optional[List[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                incident_configuration: Optional[IncidentConfiguration] = ..., 
                query: Optional[str] = ..., 
                query_frequency: Optional[timedelta] = ..., 
                query_period: Optional[timedelta] = ..., 
                sentinel_entities_mappings: Optional[List[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                suppression_duration: timedelta, 
                suppression_enabled: bool, 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                template_version: Optional[str] = ..., 
                trigger_operator: Optional[Union[str, TriggerOperator]] = ..., 
                trigger_threshold: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ScheduledAlertRuleTemplate(AlertRuleTemplate):
        alert_details_override: AlertDetailsOverride
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        custom_details: dict[str, str]
        description: str
        display_name: str
        entity_mappings: list[EntityMapping]
        event_grouping_settings: EventGroupingSettings
        id: str
        kind: Union[str, AlertRuleKind]
        last_updated_date_utc: datetime
        name: str
        query: str
        query_frequency: timedelta
        query_period: timedelta
        required_data_connectors: list[AlertRuleTemplateDataSource]
        sentinel_entities_mappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        status: Union[str, TemplateStatus]
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        trigger_operator: Union[str, TriggerOperator]
        trigger_threshold: int
        type: str
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                custom_details: Optional[Dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                entity_mappings: Optional[List[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                query: Optional[str] = ..., 
                query_frequency: Optional[timedelta] = ..., 
                query_period: Optional[timedelta] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                sentinel_entities_mappings: Optional[List[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                trigger_operator: Optional[Union[str, TriggerOperator]] = ..., 
                trigger_threshold: Optional[int] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SecurityAlert(Entity):
        additional_data: dict[str, any]
        alert_display_name: str
        alert_link: str
        alert_type: str
        compromised_entity: str
        confidence_level: Union[str, ConfidenceLevel]
        confidence_reasons: list[SecurityAlertPropertiesConfidenceReasonsItem]
        confidence_score: float
        confidence_score_status: Union[str, ConfidenceScoreStatus]
        description: str
        end_time_utc: datetime
        friendly_name: str
        id: str
        intent: Union[str, KillChainIntent]
        kind: Union[str, EntityKind]
        name: str
        processing_end_time: datetime
        product_component_name: str
        product_name: str
        product_version: str
        provider_alert_id: str
        remediation_steps: list[str]
        resource_identifiers: list[JSON]
        severity: Union[str, AlertSeverity]
        start_time_utc: datetime
        status: Union[str, AlertStatus]
        system_alert_id: str
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        time_generated: datetime
        type: str
        vendor_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SecurityAlertProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        alert_display_name: str
        alert_link: str
        alert_type: str
        compromised_entity: str
        confidence_level: Union[str, ConfidenceLevel]
        confidence_reasons: list[SecurityAlertPropertiesConfidenceReasonsItem]
        confidence_score: float
        confidence_score_status: Union[str, ConfidenceScoreStatus]
        description: str
        end_time_utc: datetime
        friendly_name: str
        intent: Union[str, KillChainIntent]
        processing_end_time: datetime
        product_component_name: str
        product_name: str
        product_version: str
        provider_alert_id: str
        remediation_steps: list[str]
        resource_identifiers: list[JSON]
        severity: Union[str, AlertSeverity]
        start_time_utc: datetime
        status: Union[str, AlertStatus]
        system_alert_id: str
        tactics: Union[list[str, AttackTactic]]
        time_generated: datetime
        vendor_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SecurityAlertPropertiesConfidenceReasonsItem(Model):
        reason: str
        reason_type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SecurityAlertTimelineItem(EntityTimelineItem):
        alert_type: str
        azure_resource_id: str
        description: str
        display_name: str
        end_time_utc: datetime
        intent: Union[str, KillChainIntent]
        kind: Union[str, EntityTimelineKind]
        product_name: str
        severity: Union[str, AlertSeverity]
        start_time_utc: datetime
        techniques: list[str]
        time_generated: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_type: str, 
                azure_resource_id: str, 
                description: Optional[str] = ..., 
                display_name: str, 
                end_time_utc: datetime, 
                product_name: Optional[str] = ..., 
                severity: Union[str, AlertSeverity], 
                start_time_utc: datetime, 
                techniques: Optional[List[str]] = ..., 
                time_generated: datetime, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SecurityGroupEntity(Entity):
        additional_data: dict[str, any]
        distinguished_name: str
        friendly_name: str
        id: str
        kind: Union[str, EntityKind]
        name: str
        object_guid: str
        sid: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SecurityGroupEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        distinguished_name: str
        friendly_name: str
        object_guid: str
        sid: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SecurityMLAnalyticsSetting(ResourceWithEtag):
        etag: str
        id: str
        kind: Union[str, SecurityMLAnalyticsSettingsKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SecurityMLAnalyticsSettingsDataSource(Model):
        connector_id: str
        data_types: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                connector_id: Optional[str] = ..., 
                data_types: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SecurityMLAnalyticsSettingsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANOMALY = "Anomaly"


    class azure.mgmt.securityinsight.models.SecurityMLAnalyticsSettingsList(Model):
        next_link: str
        value: list[SecurityMLAnalyticsSetting]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[SecurityMLAnalyticsSetting], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SentinelEntityMapping(Model):
        column_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                column_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SentinelOnboardingState(ResourceWithEtag):
        customer_managed_key: bool
        etag: str
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                customer_managed_key: Optional[bool] = ..., 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SentinelOnboardingStatesList(Model):
        value: list[SentinelOnboardingState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[SentinelOnboardingState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANOMALIES = "Anomalies"
        ENTITY_ANALYTICS = "EntityAnalytics"
        EYES_ON = "EyesOn"
        UEBA = "Ueba"


    class azure.mgmt.securityinsight.models.SettingList(Model):
        value: list[Settings]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[Settings], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SettingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPYABLE_LABEL = "CopyableLabel"
        INFO_MESSAGE = "InfoMessage"
        INSTRUCTION_STEPS_GROUP = "InstructionStepsGroup"


    class azure.mgmt.securityinsight.models.Settings(ResourceWithEtag):
        etag: str
        id: str
        kind: Union[str, SettingKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SettingsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLIGHTING = "Flighting"
        PRODUCTION = "Production"


    class azure.mgmt.securityinsight.models.SourceControl(ResourceWithEtag):
        content_types: Union[list[str, ContentType]]
        description: str
        display_name: str
        etag: str
        id: str
        id_properties_id: str
        last_deployment_info: DeploymentInfo
        name: str
        repo_type: Union[str, RepoType]
        repository: Repository
        repository_resource_info: RepositoryResourceInfo
        system_data: SystemData
        type: str
        version: Union[str, Version]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content_types: Optional[List[Union[str, ContentType]]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                id_properties_id: Optional[str] = ..., 
                last_deployment_info: Optional[DeploymentInfo] = ..., 
                repo_type: Optional[Union[str, RepoType]] = ..., 
                repository: Optional[Repository] = ..., 
                repository_resource_info: Optional[RepositoryResourceInfo] = ..., 
                version: Optional[Union[str, Version]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SourceControlList(Model):
        next_link: str
        value: list[SourceControl]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[SourceControl], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMUNITY = "Community"
        LOCAL_WORKSPACE = "LocalWorkspace"
        SOLUTION = "Solution"
        SOURCE_REPOSITORY = "SourceRepository"


    class azure.mgmt.securityinsight.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL_FILE = "Local file"
        REMOTE_STORAGE = "Remote storage"


    class azure.mgmt.securityinsight.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        COMPLETED_BY_ACTION = "CompletedByAction"
        COMPLETED_BY_USER = "CompletedByUser"
        DISABLED = "Disabled"
        HIDDEN = "Hidden"


    class azure.mgmt.securityinsight.models.SubmissionMailEntity(Entity):
        additional_data: dict[str, any]
        friendly_name: str
        id: str
        kind: Union[str, EntityKind]
        name: str
        network_message_id: str
        recipient: str
        report_type: str
        sender: str
        sender_ip: str
        subject: str
        submission_date: datetime
        submission_id: str
        submitter: str
        system_data: SystemData
        timestamp: datetime
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SubmissionMailEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        network_message_id: str
        recipient: str
        report_type: str
        sender: str
        sender_ip: str
        subject: str
        submission_date: datetime
        submission_id: str
        submitter: str
        timestamp: datetime

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.SupportTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMUNITY = "Community"
        MICROSOFT = "Microsoft"
        PARTNER = "Partner"


    class azure.mgmt.securityinsight.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TICheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TICheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TIDataConnector(DataConnector):
        data_types: TIDataConnectorDataTypes
        etag: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        system_data: SystemData
        tenant_id: str
        tip_lookback_period: datetime
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: Optional[TIDataConnectorDataTypes] = ..., 
                etag: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                tip_lookback_period: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TIDataConnectorDataTypes(Model):
        indicators: TIDataConnectorDataTypesIndicators

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                indicators: TIDataConnectorDataTypesIndicators, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TIDataConnectorDataTypesIndicators(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TIDataConnectorProperties(DataConnectorTenantId):
        data_types: TIDataConnectorDataTypes
        tenant_id: str
        tip_lookback_period: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_types: TIDataConnectorDataTypes, 
                tenant_id: str, 
                tip_lookback_period: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TeamInformation(Model):
        description: str
        name: str
        primary_channel_url: str
        team_creation_time_utc: datetime
        team_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TeamProperties(Model):
        group_ids: list[str]
        member_ids: list[str]
        team_description: str
        team_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                group_ids: Optional[List[str]] = ..., 
                member_ids: Optional[List[str]] = ..., 
                team_description: Optional[str] = ..., 
                team_name: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TemplateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        INSTALLED = "Installed"
        NOT_AVAILABLE = "NotAvailable"


    class azure.mgmt.securityinsight.models.ThreatIntelligence(Model):
        confidence: float
        provider_name: str
        report_link: str
        threat_description: str
        threat_name: str
        threat_type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceAlertRule(AlertRule):
        alert_rule_template_name: str
        description: str
        display_name: str
        enabled: bool
        etag: str
        id: str
        kind: Union[str, AlertRuleKind]
        last_modified_utc: datetime
        name: str
        severity: Union[str, AlertSeverity]
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rule_template_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceAlertRuleTemplate(AlertRuleTemplate):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        id: str
        kind: Union[str, AlertRuleKind]
        last_updated_date_utc: datetime
        name: str
        required_data_connectors: list[AlertRuleTemplateDataSource]
        severity: Union[str, AlertSeverity]
        status: Union[str, TemplateStatus]
        system_data: SystemData
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceAlertRuleTemplateProperties(AlertRuleTemplateWithMitreProperties):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        last_updated_date_utc: datetime
        required_data_connectors: list[AlertRuleTemplateDataSource]
        severity: Union[str, AlertSeverity]
        status: Union[str, TemplateStatus]
        tactics: Union[list[str, AttackTactic]]
        techniques: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[List[AlertRuleTemplateDataSource]] = ..., 
                severity: Union[str, AlertSeverity], 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[List[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceAppendTags(Model):
        threat_intelligence_tags: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                threat_intelligence_tags: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceExternalReference(Model):
        description: str
        external_id: str
        hashes: dict[str, str]
        source_name: str
        url: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                external_id: Optional[str] = ..., 
                hashes: Optional[Dict[str, str]] = ..., 
                source_name: Optional[str] = ..., 
                url: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceFilteringCriteria(Model):
        ids: list[str]
        include_disabled: bool
        keywords: list[str]
        max_confidence: int
        max_valid_until: str
        min_confidence: int
        min_valid_until: str
        page_size: int
        pattern_types: list[str]
        skip_token: str
        sort_by: list[ThreatIntelligenceSortingCriteria]
        sources: list[str]
        threat_types: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                ids: Optional[List[str]] = ..., 
                include_disabled: Optional[bool] = ..., 
                keywords: Optional[List[str]] = ..., 
                max_confidence: Optional[int] = ..., 
                max_valid_until: Optional[str] = ..., 
                min_confidence: Optional[int] = ..., 
                min_valid_until: Optional[str] = ..., 
                page_size: Optional[int] = ..., 
                pattern_types: Optional[List[str]] = ..., 
                skip_token: Optional[str] = ..., 
                sort_by: Optional[List[ThreatIntelligenceSortingCriteria]] = ..., 
                sources: Optional[List[str]] = ..., 
                threat_types: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceGranularMarkingModel(Model):
        language: str
        marking_ref: int
        selectors: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                marking_ref: Optional[int] = ..., 
                selectors: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceIndicatorModel(ThreatIntelligenceInformation):
        additional_data: dict[str, any]
        confidence: int
        created: str
        created_by_ref: str
        defanged: bool
        description: str
        display_name: str
        etag: str
        extensions: dict[str, any]
        external_id: str
        external_last_updated_time_utc: str
        external_references: list[ThreatIntelligenceExternalReference]
        friendly_name: str
        granular_markings: list[ThreatIntelligenceGranularMarkingModel]
        id: str
        indicator_types: list[str]
        kill_chain_phases: list[ThreatIntelligenceKillChainPhase]
        kind: Union[str, ThreatIntelligenceResourceKindEnum]
        labels: list[str]
        language: str
        last_updated_time_utc: str
        modified: str
        name: str
        object_marking_refs: list[str]
        parsed_pattern: list[ThreatIntelligenceParsedPattern]
        pattern: str
        pattern_type: str
        pattern_version: str
        revoked: bool
        source: str
        system_data: SystemData
        threat_intelligence_tags: list[str]
        threat_types: list[str]
        type: str
        valid_from: str
        valid_until: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                confidence: Optional[int] = ..., 
                created: Optional[str] = ..., 
                created_by_ref: Optional[str] = ..., 
                defanged: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                extensions: Optional[Dict[str, Any]] = ..., 
                external_id: Optional[str] = ..., 
                external_last_updated_time_utc: Optional[str] = ..., 
                external_references: Optional[List[ThreatIntelligenceExternalReference]] = ..., 
                granular_markings: Optional[List[ThreatIntelligenceGranularMarkingModel]] = ..., 
                indicator_types: Optional[List[str]] = ..., 
                kill_chain_phases: Optional[List[ThreatIntelligenceKillChainPhase]] = ..., 
                labels: Optional[List[str]] = ..., 
                language: Optional[str] = ..., 
                last_updated_time_utc: Optional[str] = ..., 
                modified: Optional[str] = ..., 
                object_marking_refs: Optional[List[str]] = ..., 
                parsed_pattern: Optional[List[ThreatIntelligenceParsedPattern]] = ..., 
                pattern: Optional[str] = ..., 
                pattern_type: Optional[str] = ..., 
                pattern_version: Optional[str] = ..., 
                revoked: Optional[bool] = ..., 
                source: Optional[str] = ..., 
                threat_intelligence_tags: Optional[List[str]] = ..., 
                threat_types: Optional[List[str]] = ..., 
                valid_from: Optional[str] = ..., 
                valid_until: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceIndicatorProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        confidence: int
        created: str
        created_by_ref: str
        defanged: bool
        description: str
        display_name: str
        extensions: dict[str, any]
        external_id: str
        external_last_updated_time_utc: str
        external_references: list[ThreatIntelligenceExternalReference]
        friendly_name: str
        granular_markings: list[ThreatIntelligenceGranularMarkingModel]
        indicator_types: list[str]
        kill_chain_phases: list[ThreatIntelligenceKillChainPhase]
        labels: list[str]
        language: str
        last_updated_time_utc: str
        modified: str
        object_marking_refs: list[str]
        parsed_pattern: list[ThreatIntelligenceParsedPattern]
        pattern: str
        pattern_type: str
        pattern_version: str
        revoked: bool
        source: str
        threat_intelligence_tags: list[str]
        threat_types: list[str]
        valid_from: str
        valid_until: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                confidence: Optional[int] = ..., 
                created: Optional[str] = ..., 
                created_by_ref: Optional[str] = ..., 
                defanged: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                extensions: Optional[Dict[str, Any]] = ..., 
                external_id: Optional[str] = ..., 
                external_last_updated_time_utc: Optional[str] = ..., 
                external_references: Optional[List[ThreatIntelligenceExternalReference]] = ..., 
                granular_markings: Optional[List[ThreatIntelligenceGranularMarkingModel]] = ..., 
                indicator_types: Optional[List[str]] = ..., 
                kill_chain_phases: Optional[List[ThreatIntelligenceKillChainPhase]] = ..., 
                labels: Optional[List[str]] = ..., 
                language: Optional[str] = ..., 
                last_updated_time_utc: Optional[str] = ..., 
                modified: Optional[str] = ..., 
                object_marking_refs: Optional[List[str]] = ..., 
                parsed_pattern: Optional[List[ThreatIntelligenceParsedPattern]] = ..., 
                pattern: Optional[str] = ..., 
                pattern_type: Optional[str] = ..., 
                pattern_version: Optional[str] = ..., 
                revoked: Optional[bool] = ..., 
                source: Optional[str] = ..., 
                threat_intelligence_tags: Optional[List[str]] = ..., 
                threat_types: Optional[List[str]] = ..., 
                valid_from: Optional[str] = ..., 
                valid_until: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceInformation(ResourceWithEtag):
        etag: str
        id: str
        kind: Union[str, ThreatIntelligenceResourceKindEnum]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceInformationList(Model):
        next_link: str
        value: list[ThreatIntelligenceInformation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[ThreatIntelligenceInformation], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceKillChainPhase(Model):
        kill_chain_name: str
        phase_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                kill_chain_name: Optional[str] = ..., 
                phase_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceMetric(Model):
        last_updated_time_utc: str
        pattern_type_metrics: list[ThreatIntelligenceMetricEntity]
        source_metrics: list[ThreatIntelligenceMetricEntity]
        threat_type_metrics: list[ThreatIntelligenceMetricEntity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                last_updated_time_utc: Optional[str] = ..., 
                pattern_type_metrics: Optional[List[ThreatIntelligenceMetricEntity]] = ..., 
                source_metrics: Optional[List[ThreatIntelligenceMetricEntity]] = ..., 
                threat_type_metrics: Optional[List[ThreatIntelligenceMetricEntity]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceMetricEntity(Model):
        metric_name: str
        metric_value: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                metric_name: Optional[str] = ..., 
                metric_value: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceMetrics(Model):
        properties: ThreatIntelligenceMetric

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[ThreatIntelligenceMetric] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceMetricsList(Model):
        value: list[ThreatIntelligenceMetrics]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[ThreatIntelligenceMetrics], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceParsedPattern(Model):
        pattern_type_key: str
        pattern_type_values: list[ThreatIntelligenceParsedPatternTypeValue]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                pattern_type_key: Optional[str] = ..., 
                pattern_type_values: Optional[List[ThreatIntelligenceParsedPatternTypeValue]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceParsedPatternTypeValue(Model):
        value: str
        value_type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[str] = ..., 
                value_type: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceResourceKindEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INDICATOR = "indicator"


    class azure.mgmt.securityinsight.models.ThreatIntelligenceSortingCriteria(Model):
        item_key: str
        sort_order: Union[str, ThreatIntelligenceSortingCriteriaEnum]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                item_key: Optional[str] = ..., 
                sort_order: Optional[Union[str, ThreatIntelligenceSortingCriteriaEnum]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceSortingCriteriaEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCENDING = "ascending"
        DESCENDING = "descending"
        UNSORTED = "unsorted"


    class azure.mgmt.securityinsight.models.TiTaxiiCheckRequirements(DataConnectorsCheckRequirements):
        kind: Union[str, DataConnectorKind]
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TiTaxiiCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tenant_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TiTaxiiDataConnector(DataConnector):
        collection_id: str
        data_types: TiTaxiiDataConnectorDataTypes
        etag: str
        friendly_name: str
        id: str
        kind: Union[str, DataConnectorKind]
        name: str
        password: str
        polling_frequency: Union[str, PollingFrequency]
        system_data: SystemData
        taxii_lookback_period: datetime
        taxii_server: str
        tenant_id: str
        type: str
        user_name: str
        workspace_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                collection_id: Optional[str] = ..., 
                data_types: Optional[TiTaxiiDataConnectorDataTypes] = ..., 
                etag: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                password: Optional[str] = ..., 
                polling_frequency: Optional[Union[str, PollingFrequency]] = ..., 
                taxii_lookback_period: Optional[datetime] = ..., 
                taxii_server: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                user_name: Optional[str] = ..., 
                workspace_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TiTaxiiDataConnectorDataTypes(Model):
        taxii_client: TiTaxiiDataConnectorDataTypesTaxiiClient

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                taxii_client: TiTaxiiDataConnectorDataTypesTaxiiClient, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TiTaxiiDataConnectorDataTypesTaxiiClient(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TiTaxiiDataConnectorProperties(DataConnectorTenantId):
        collection_id: str
        data_types: TiTaxiiDataConnectorDataTypes
        friendly_name: str
        password: str
        polling_frequency: Union[str, PollingFrequency]
        taxii_lookback_period: datetime
        taxii_server: str
        tenant_id: str
        user_name: str
        workspace_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                collection_id: Optional[str] = ..., 
                data_types: TiTaxiiDataConnectorDataTypes, 
                friendly_name: Optional[str] = ..., 
                password: Optional[str] = ..., 
                polling_frequency: Union[str, PollingFrequency], 
                taxii_lookback_period: Optional[datetime] = ..., 
                taxii_server: Optional[str] = ..., 
                tenant_id: str, 
                user_name: Optional[str] = ..., 
                workspace_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TimelineAggregation(Model):
        count: int
        kind: Union[str, EntityTimelineKind]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                count: int, 
                kind: Union[str, EntityTimelineKind], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TimelineError(Model):
        error_message: str
        kind: Union[str, EntityTimelineKind]
        query_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error_message: str, 
                kind: Union[str, EntityTimelineKind], 
                query_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TimelineResultsMetadata(Model):
        aggregations: list[TimelineAggregation]
        errors: list[TimelineError]
        total_count: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                aggregations: List[TimelineAggregation], 
                errors: Optional[List[TimelineError]] = ..., 
                total_count: int, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.TriggerOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        LESS_THAN = "LessThan"
        NOT_EQUAL = "NotEqual"


    class azure.mgmt.securityinsight.models.TriggersOn(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"
        INCIDENTS = "Incidents"


    class azure.mgmt.securityinsight.models.TriggersWhen(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        UPDATED = "Updated"


    class azure.mgmt.securityinsight.models.Ueba(Settings):
        data_sources: Union[list[str, UebaDataSources]]
        etag: str
        id: str
        kind: Union[str, SettingKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data_sources: Optional[List[Union[str, UebaDataSources]]] = ..., 
                etag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.UebaDataSources(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT_LOGS = "AuditLogs"
        AZURE_ACTIVITY = "AzureActivity"
        SECURITY_EVENT = "SecurityEvent"
        SIGNIN_LOGS = "SigninLogs"


    class azure.mgmt.securityinsight.models.UrlEntity(Entity):
        additional_data: dict[str, any]
        friendly_name: str
        id: str
        kind: Union[str, EntityKind]
        name: str
        system_data: SystemData
        type: str
        url: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.UrlEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        url: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.UserInfo(Model):
        email: str
        name: str
        object_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.ValidationError(Model):
        error_messages: list[str]
        record_index: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                record_index: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Version(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V1 = "V1"
        V2 = "V2"


    class azure.mgmt.securityinsight.models.Watchlist(ResourceWithEtag):
        content_type: str
        created: datetime
        created_by: UserInfo
        default_duration: timedelta
        description: str
        display_name: str
        etag: str
        id: str
        is_deleted: bool
        items_search_key: str
        labels: list[str]
        name: str
        number_of_lines_to_skip: int
        provider: str
        raw_content: str
        source: str
        source_type: Union[str, SourceType]
        system_data: SystemData
        tenant_id: str
        type: str
        updated: datetime
        updated_by: UserInfo
        upload_status: str
        watchlist_alias: str
        watchlist_id: str
        watchlist_type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content_type: Optional[str] = ..., 
                created: Optional[datetime] = ..., 
                created_by: Optional[UserInfo] = ..., 
                default_duration: Optional[timedelta] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                is_deleted: Optional[bool] = ..., 
                items_search_key: Optional[str] = ..., 
                labels: Optional[List[str]] = ..., 
                number_of_lines_to_skip: Optional[int] = ..., 
                provider: Optional[str] = ..., 
                raw_content: Optional[str] = ..., 
                source: Optional[str] = ..., 
                source_type: Optional[Union[str, SourceType]] = ..., 
                tenant_id: Optional[str] = ..., 
                updated: Optional[datetime] = ..., 
                updated_by: Optional[UserInfo] = ..., 
                upload_status: Optional[str] = ..., 
                watchlist_alias: Optional[str] = ..., 
                watchlist_id: Optional[str] = ..., 
                watchlist_type: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.WatchlistItem(ResourceWithEtag):
        created: datetime
        created_by: UserInfo
        entity_mapping: dict[str, any]
        etag: str
        id: str
        is_deleted: bool
        items_key_value: dict[str, any]
        name: str
        system_data: SystemData
        tenant_id: str
        type: str
        updated: datetime
        updated_by: UserInfo
        watchlist_item_id: str
        watchlist_item_type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                created_by: Optional[UserInfo] = ..., 
                entity_mapping: Optional[Dict[str, Any]] = ..., 
                etag: Optional[str] = ..., 
                is_deleted: Optional[bool] = ..., 
                items_key_value: Optional[Dict[str, Any]] = ..., 
                tenant_id: Optional[str] = ..., 
                updated: Optional[datetime] = ..., 
                updated_by: Optional[UserInfo] = ..., 
                watchlist_item_id: Optional[str] = ..., 
                watchlist_item_type: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.WatchlistItemList(Model):
        next_link: str
        value: list[WatchlistItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[WatchlistItem], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.WatchlistList(Model):
        next_link: str
        value: list[Watchlist]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: List[Watchlist], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securityinsight.models.Webhook(Model):
        rotate_webhook_secret: bool
        webhook_id: str
        webhook_secret_update_time: str
        webhook_url: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                rotate_webhook_secret: Optional[bool] = ..., 
                webhook_id: Optional[str] = ..., 
                webhook_secret_update_time: Optional[str] = ..., 
                webhook_url: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


namespace azure.mgmt.securityinsight.operations

    class azure.mgmt.securityinsight.operations.ActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                action_id: str, 
                action: ActionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionResponse: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                action_id: str, 
                action: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ActionResponse: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                action_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                action_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ActionResponse: ...

        @distributed_trace
        def list_by_alert_rule(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ActionResponse]: ...


    class azure.mgmt.securityinsight.operations.AlertRuleTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                alert_rule_template_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertRuleTemplate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AlertRuleTemplate]: ...


    class azure.mgmt.securityinsight.operations.AlertRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                alert_rule: AlertRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                alert_rule: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertRule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AlertRule]: ...


    class azure.mgmt.securityinsight.operations.AutomationRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                automation_rule_id: str, 
                automation_rule_to_upsert: Optional[AutomationRule] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                automation_rule_id: str, 
                automation_rule_to_upsert: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationRule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                automation_rule_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                automation_rule_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AutomationRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AutomationRule]: ...


    class azure.mgmt.securityinsight.operations.BookmarkOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def expand(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                parameters: BookmarkExpandParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BookmarkExpandResponse: ...

        @overload
        def expand(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BookmarkExpandResponse: ...


    class azure.mgmt.securityinsight.operations.BookmarkRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                relation: Relation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Relation: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                relation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Relation]: ...


    class azure.mgmt.securityinsight.operations.BookmarksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                bookmark: Bookmark, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bookmark: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                bookmark: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Bookmark: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Bookmark: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Bookmark]: ...


    class azure.mgmt.securityinsight.operations.DataConnectorsCheckRequirementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connectors_check_requirements: DataConnectorsCheckRequirements, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorRequirementsState: ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connectors_check_requirements: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorRequirementsState: ...


    class azure.mgmt.securityinsight.operations.DataConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def connect(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                connect_body: DataConnectorConnectBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def connect(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                connect_body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                data_connector: DataConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnector: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                data_connector: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnector: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disconnect(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataConnector: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataConnector]: ...


    class azure.mgmt.securityinsight.operations.DomainWhoisOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnrichmentDomainWhois: ...


    class azure.mgmt.securityinsight.operations.EntitiesGetTimelineOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: EntityTimelineParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityTimelineResponse: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityTimelineResponse: ...


    class azure.mgmt.securityinsight.operations.EntitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def expand(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: EntityExpandParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityExpandResponse: ...

        @overload
        def expand(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityExpandResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Entity: ...

        @overload
        def get_insights(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: EntityGetInsightsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityGetInsightsResponse: ...

        @overload
        def get_insights(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityGetInsightsResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Entity]: ...

        @distributed_trace
        def queries(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                kind: Union[str, EntityItemQueryKind], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GetQueriesResponse: ...


    class azure.mgmt.securityinsight.operations.EntitiesRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Relation]: ...


    class azure.mgmt.securityinsight.operations.EntityQueriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                entity_query: CustomEntityQuery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityQuery: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                entity_query: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityQuery: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EntityQuery: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kind: Optional[Union[str, Enum13]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[EntityQuery]: ...


    class azure.mgmt.securityinsight.operations.EntityQueryTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_template_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EntityQueryTemplate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kind: Optional[Union[str, Enum15]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[EntityQueryTemplate]: ...


    class azure.mgmt.securityinsight.operations.EntityRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_relation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                relation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Relation: ...


    class azure.mgmt.securityinsight.operations.FileImportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[FileImport]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
                file_import: FileImport, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileImport: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
                file_import: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileImport: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> FileImport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[FileImport]: ...


    class azure.mgmt.securityinsight.operations.GetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def single_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Recommendation: ...


    class azure.mgmt.securityinsight.operations.GetRecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RecommendationList: ...


    class azure.mgmt.securityinsight.operations.IPGeodataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ip_address: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnrichmentIpGeodata: ...


    class azure.mgmt.securityinsight.operations.IncidentCommentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_comment_id: str, 
                incident_comment: IncidentComment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IncidentComment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_comment_id: str, 
                incident_comment: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IncidentComment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_comment_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_comment_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IncidentComment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IncidentComment]: ...


    class azure.mgmt.securityinsight.operations.IncidentRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                relation_name: str, 
                relation: Relation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Relation: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                relation_name: str, 
                relation: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                relation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                relation_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Relation]: ...


    class azure.mgmt.securityinsight.operations.IncidentTasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_task_id: str, 
                incident_task: IncidentTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IncidentTask: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_task_id: str, 
                incident_task: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IncidentTask: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_task_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_task_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IncidentTask: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IncidentTask]: ...


    class azure.mgmt.securityinsight.operations.IncidentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident: Incident, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Incident: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Incident: ...

        @overload
        def create_team(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                team_properties: TeamInformation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TeamInformation: ...

        @overload
        def create_team(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                team_properties: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TeamInformation: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Incident: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Incident]: ...

        @distributed_trace
        def list_alerts(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IncidentAlertList: ...

        @distributed_trace
        def list_bookmarks(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IncidentBookmarkList: ...

        @distributed_trace
        def list_entities(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IncidentEntitiesResponse: ...

        @overload
        def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_identifier: str, 
                request_body: Optional[ManualTriggerRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_identifier: str, 
                request_body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.securityinsight.operations.MetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                metadata: MetadataModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataModel: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                metadata: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataModel: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MetadataModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[MetadataModel]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                metadata_patch: MetadataPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataModel: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                metadata_patch: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataModel: ...


    class azure.mgmt.securityinsight.operations.OfficeConsentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                consent_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                consent_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OfficeConsent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[OfficeConsent]: ...


    class azure.mgmt.securityinsight.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Operation]: ...


    class azure.mgmt.securityinsight.operations.ProductSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Settings: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SettingList: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                settings: Settings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                settings: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...


    class azure.mgmt.securityinsight.operations.SecurityMLAnalyticsSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_resource_name: str, 
                security_ml_analytics_setting: SecurityMLAnalyticsSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityMLAnalyticsSetting: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_resource_name: str, 
                security_ml_analytics_setting: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityMLAnalyticsSetting: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SecurityMLAnalyticsSetting: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SecurityMLAnalyticsSetting]: ...


    class azure.mgmt.securityinsight.operations.SentinelOnboardingStatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sentinel_onboarding_state_name: str, 
                sentinel_onboarding_state_parameter: Optional[SentinelOnboardingState] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SentinelOnboardingState: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sentinel_onboarding_state_name: str, 
                sentinel_onboarding_state_parameter: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SentinelOnboardingState: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sentinel_onboarding_state_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sentinel_onboarding_state_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SentinelOnboardingState: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SentinelOnboardingStatesList: ...


    class azure.mgmt.securityinsight.operations.SourceControlOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_repositories(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                repo_type: Union[str, RepoType], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Repo]: ...


    class azure.mgmt.securityinsight.operations.SourceControlsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                source_control: SourceControl, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                source_control: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SourceControl]: ...


    class azure.mgmt.securityinsight.operations.ThreatIntelligenceIndicatorMetricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ThreatIntelligenceMetricsList: ...


    class azure.mgmt.securityinsight.operations.ThreatIntelligenceIndicatorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def append_tags(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_append_tags: ThreatIntelligenceAppendTags, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def append_tags(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_append_tags: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_properties: ThreatIntelligenceIndicatorModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_properties: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @overload
        def create_indicator(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_properties: ThreatIntelligenceIndicatorModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @overload
        def create_indicator(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_properties: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @overload
        def query_indicators(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_filtering_criteria: ThreatIntelligenceFilteringCriteria, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[ThreatIntelligenceInformation]: ...

        @overload
        def query_indicators(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_filtering_criteria: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[ThreatIntelligenceInformation]: ...

        @overload
        def replace_tags(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_replace_tags: ThreatIntelligenceIndicatorModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...

        @overload
        def replace_tags(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                threat_intelligence_replace_tags: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...


    class azure.mgmt.securityinsight.operations.ThreatIntelligenceIndicatorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ThreatIntelligenceInformation]: ...


    class azure.mgmt.securityinsight.operations.UpdateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                recommendation_patch: List[RecommendationPatch], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Recommendation]: ...

        @overload
        def begin_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                recommendation_patch: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Recommendation]: ...


    class azure.mgmt.securityinsight.operations.WatchlistItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist_item_id: str, 
                watchlist_item: WatchlistItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WatchlistItem: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist_item_id: str, 
                watchlist_item: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WatchlistItem: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist_item_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist_item_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WatchlistItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WatchlistItem]: ...


    class azure.mgmt.securityinsight.operations.WatchlistsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist: Watchlist, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watchlist: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watchlist: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Watchlist: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Watchlist]: ...


```