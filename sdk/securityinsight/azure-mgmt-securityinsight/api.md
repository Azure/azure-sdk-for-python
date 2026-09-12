```py
namespace azure.mgmt.securityinsight

    class azure.mgmt.securityinsight.SecurityInsightsMgmtClient(_SecurityInsightsMgmtClientOperationsMixin): implements ContextManager 
        actions: ActionsOperations
        alert_rule: AlertRuleOperations
        alert_rule_templates: AlertRuleTemplatesOperations
        alert_rules: AlertRulesOperations
        automation_rules: AutomationRulesOperations
        billing_statistics: BillingStatisticsOperations
        bookmark: BookmarkOperations
        bookmark_relations: BookmarkRelationsOperations
        bookmarks: BookmarksOperations
        content_package: ContentPackageOperations
        content_packages: ContentPackagesOperations
        content_template: ContentTemplateOperations
        content_templates: ContentTemplatesOperations
        data_connector_definitions: DataConnectorDefinitionsOperations
        data_connectors: DataConnectorsOperations
        data_connectors_check_requirements: DataConnectorsCheckRequirementsOperations
        entities: EntitiesOperations
        entities_get_timeline: EntitiesGetTimelineOperations
        entities_relations: EntitiesRelationsOperations
        entity_queries: EntityQueriesOperations
        entity_query_templates: EntityQueryTemplatesOperations
        entity_relations: EntityRelationsOperations
        file_imports: FileImportsOperations
        get: GetOperations
        get_recommendations: GetRecommendationsOperations
        get_triggered_analytics_rule_runs: GetTriggeredAnalyticsRuleRunsOperations
        hunt_comments: HuntCommentsOperations
        hunt_relations: HuntRelationsOperations
        hunts: HuntsOperations
        incident_comments: IncidentCommentsOperations
        incident_relations: IncidentRelationsOperations
        incident_tasks: IncidentTasksOperations
        incidents: IncidentsOperations
        metadata: MetadataOperations
        office_consents: OfficeConsentsOperations
        operations: Operations
        product_package: ProductPackageOperations
        product_packages: ProductPackagesOperations
        product_settings: ProductSettingsOperations
        product_template: ProductTemplateOperations
        product_templates: ProductTemplatesOperations
        reevaluate: ReevaluateOperations
        security_ml_analytics_settings: SecurityMLAnalyticsSettingsOperations
        sentinel_onboarding_states: SentinelOnboardingStatesOperations
        source_control: SourceControlOperations
        source_controls: SourceControlsOperations
        threat_intelligence: ThreatIntelligenceOperations
        threat_intelligence_indicator: ThreatIntelligenceIndicatorOperations
        threat_intelligence_indicator_metrics: ThreatIntelligenceIndicatorMetricsOperations
        threat_intelligence_indicators: ThreatIntelligenceIndicatorsOperations
        triggered_analytics_rule_run: TriggeredAnalyticsRuleRunOperations
        update: UpdateOperations
        watchlist_items: WatchlistItemsOperations
        watchlists: WatchlistsOperations
        workspace_manager_assignment_jobs: WorkspaceManagerAssignmentJobsOperations
        workspace_manager_assignments: WorkspaceManagerAssignmentsOperations
        workspace_manager_configurations: WorkspaceManagerConfigurationsOperations
        workspace_manager_groups: WorkspaceManagerGroupsOperations
        workspace_manager_members: WorkspaceManagerMembersOperations

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

        @overload
        def list_geodata_by_ip(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                ip_address_body: EnrichmentIpAddressBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentIpGeodata: ...

        @overload
        def list_geodata_by_ip(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                ip_address_body: EnrichmentIpAddressBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentIpGeodata: ...

        @overload
        def list_geodata_by_ip(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                ip_address_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentIpGeodata: ...

        @overload
        def list_whois_by_domain(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                domain_body: EnrichmentDomainBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentDomainWhois: ...

        @overload
        def list_whois_by_domain(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                domain_body: EnrichmentDomainBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentDomainWhois: ...

        @overload
        def list_whois_by_domain(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                domain_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentDomainWhois: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.securityinsight.aio

    class azure.mgmt.securityinsight.aio.SecurityInsightsMgmtClient(_SecurityInsightsMgmtClientOperationsMixin): implements AsyncContextManager 
        actions: ActionsOperations
        alert_rule: AlertRuleOperations
        alert_rule_templates: AlertRuleTemplatesOperations
        alert_rules: AlertRulesOperations
        automation_rules: AutomationRulesOperations
        billing_statistics: BillingStatisticsOperations
        bookmark: BookmarkOperations
        bookmark_relations: BookmarkRelationsOperations
        bookmarks: BookmarksOperations
        content_package: ContentPackageOperations
        content_packages: ContentPackagesOperations
        content_template: ContentTemplateOperations
        content_templates: ContentTemplatesOperations
        data_connector_definitions: DataConnectorDefinitionsOperations
        data_connectors: DataConnectorsOperations
        data_connectors_check_requirements: DataConnectorsCheckRequirementsOperations
        entities: EntitiesOperations
        entities_get_timeline: EntitiesGetTimelineOperations
        entities_relations: EntitiesRelationsOperations
        entity_queries: EntityQueriesOperations
        entity_query_templates: EntityQueryTemplatesOperations
        entity_relations: EntityRelationsOperations
        file_imports: FileImportsOperations
        get: GetOperations
        get_recommendations: GetRecommendationsOperations
        get_triggered_analytics_rule_runs: GetTriggeredAnalyticsRuleRunsOperations
        hunt_comments: HuntCommentsOperations
        hunt_relations: HuntRelationsOperations
        hunts: HuntsOperations
        incident_comments: IncidentCommentsOperations
        incident_relations: IncidentRelationsOperations
        incident_tasks: IncidentTasksOperations
        incidents: IncidentsOperations
        metadata: MetadataOperations
        office_consents: OfficeConsentsOperations
        operations: Operations
        product_package: ProductPackageOperations
        product_packages: ProductPackagesOperations
        product_settings: ProductSettingsOperations
        product_template: ProductTemplateOperations
        product_templates: ProductTemplatesOperations
        reevaluate: ReevaluateOperations
        security_ml_analytics_settings: SecurityMLAnalyticsSettingsOperations
        sentinel_onboarding_states: SentinelOnboardingStatesOperations
        source_control: SourceControlOperations
        source_controls: SourceControlsOperations
        threat_intelligence: ThreatIntelligenceOperations
        threat_intelligence_indicator: ThreatIntelligenceIndicatorOperations
        threat_intelligence_indicator_metrics: ThreatIntelligenceIndicatorMetricsOperations
        threat_intelligence_indicators: ThreatIntelligenceIndicatorsOperations
        triggered_analytics_rule_run: TriggeredAnalyticsRuleRunOperations
        update: UpdateOperations
        watchlist_items: WatchlistItemsOperations
        watchlists: WatchlistsOperations
        workspace_manager_assignment_jobs: WorkspaceManagerAssignmentJobsOperations
        workspace_manager_assignments: WorkspaceManagerAssignmentsOperations
        workspace_manager_configurations: WorkspaceManagerConfigurationsOperations
        workspace_manager_groups: WorkspaceManagerGroupsOperations
        workspace_manager_members: WorkspaceManagerMembersOperations

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

        @overload
        async def list_geodata_by_ip(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                ip_address_body: EnrichmentIpAddressBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentIpGeodata: ...

        @overload
        async def list_geodata_by_ip(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                ip_address_body: EnrichmentIpAddressBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentIpGeodata: ...

        @overload
        async def list_geodata_by_ip(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                ip_address_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentIpGeodata: ...

        @overload
        async def list_whois_by_domain(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                domain_body: EnrichmentDomainBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentDomainWhois: ...

        @overload
        async def list_whois_by_domain(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                domain_body: EnrichmentDomainBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentDomainWhois: ...

        @overload
        async def list_whois_by_domain(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                enrichment_type: Union[str, EnrichmentType], 
                domain_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnrichmentDomainWhois: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


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
                action: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                action_id: str, 
                **kwargs: Any
            ) -> ActionResponse: ...

        @distributed_trace
        def list_by_alert_rule(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ActionResponse]: ...


    class azure.mgmt.securityinsight.aio.operations.AlertRuleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_trigger_rule_run(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                analytics_rule_run_trigger_parameter: AnalyticsRuleRunTrigger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_rule_run(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                analytics_rule_run_trigger_parameter: AnalyticsRuleRunTrigger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_trigger_rule_run(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                analytics_rule_run_trigger_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


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
                **kwargs: Any
            ) -> AlertRuleTemplate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AlertRuleTemplate]: ...


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
                alert_rule: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                **kwargs: Any
            ) -> AlertRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AlertRule]: ...


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
                automation_rule_to_upsert: Optional[IO[bytes]] = None, 
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
                **kwargs: Any
            ) -> Any: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                automation_rule_id: str, 
                **kwargs: Any
            ) -> AutomationRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutomationRule]: ...


    class azure.mgmt.securityinsight.aio.operations.BillingStatisticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'billing_statistic_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                billing_statistic_name: str, 
                **kwargs: Any
            ) -> BillingStatistic: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BillingStatistic]: ...


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
                parameters: IO[bytes], 
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
                relation: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'bookmark_id', 'relation_name']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'bookmark_id', 'relation_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'bookmark_id', 'filter', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Relation]: ...


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
                bookmark: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                **kwargs: Any
            ) -> Bookmark: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Bookmark]: ...


    class azure.mgmt.securityinsight.aio.operations.ContentPackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                package_id: str, 
                package_installation_properties: PackageModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PackageModel: ...

        @overload
        async def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                package_id: str, 
                package_installation_properties: PackageModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PackageModel: ...

        @overload
        async def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                package_id: str, 
                package_installation_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PackageModel: ...

        @distributed_trace_async
        async def uninstall(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                package_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.aio.operations.ContentPackagesOperations:

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
                package_id: str, 
                **kwargs: Any
            ) -> PackageModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PackageModel]: ...


    class azure.mgmt.securityinsight.aio.operations.ContentTemplateOperations:

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
                template_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                template_id: str, 
                **kwargs: Any
            ) -> TemplateModel: ...

        @overload
        async def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                template_id: str, 
                template_installation_properties: TemplateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateModel: ...

        @overload
        async def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                template_id: str, 
                template_installation_properties: TemplateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateModel: ...

        @overload
        async def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                template_id: str, 
                template_installation_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateModel: ...


    class azure.mgmt.securityinsight.aio.operations.ContentTemplatesOperations:

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
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TemplateModel]: ...


    class azure.mgmt.securityinsight.aio.operations.DataConnectorDefinitionsOperations:

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
                data_connector_definition_name: str, 
                connector_definition_input: DataConnectorDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorDefinition: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_definition_name: str, 
                connector_definition_input: DataConnectorDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorDefinition: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_definition_name: str, 
                connector_definition_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorDefinition: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_definition_name: str, 
                **kwargs: Any
            ) -> DataConnectorDefinition: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataConnectorDefinition]: ...


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
                data_connectors_check_requirements: IO[bytes], 
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
                connect_body: IO[bytes], 
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
                data_connector: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'data_connector_id']}, api_versions_list=['2025-10-01-preview'])
        async def disconnect(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                **kwargs: Any
            ) -> DataConnector: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataConnector]: ...


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
                parameters: IO[bytes], 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityExpandResponse: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityGetInsightsResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Entity]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_id', 'kind', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def queries(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                *, 
                kind: Union[str, EntityItemQueryKind], 
                **kwargs: Any
            ) -> AsyncItemPaged[EntityQueryItem]: ...

        @overload
        async def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_identifier: str, 
                request_body: Optional[EntityManualTriggerRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_identifier: str, 
                request_body: Optional[EntityManualTriggerRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_identifier: str, 
                request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


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
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Relation]: ...


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
                entity_query: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityQuery: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_query_id']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_query_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                **kwargs: Any
            ) -> EntityQuery: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'kind', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                kind: Optional[Union[str, EntityQueryTemplateKind]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EntityQuery]: ...


    class azure.mgmt.securityinsight.aio.operations.EntityQueryTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_query_template_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_template_id: str, 
                **kwargs: Any
            ) -> EntityQueryTemplate: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'kind', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                kind: Optional[Union[str, EntityQueryTemplateKind]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EntityQueryTemplate]: ...


    class azure.mgmt.securityinsight.aio.operations.EntityRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_id', 'relation_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get_relation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                relation_name: str, 
                **kwargs: Any
            ) -> Relation: ...


    class azure.mgmt.securityinsight.aio.operations.FileImportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'file_import_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
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
                file_import: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileImport: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'file_import_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
                **kwargs: Any
            ) -> FileImport: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'filter', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[FileImport]: ...


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
                **kwargs: Any
            ) -> Recommendation: ...


    class azure.mgmt.securityinsight.aio.operations.GetRecommendationsOperations:

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
                **kwargs: Any
            ) -> AsyncItemPaged[Recommendation]: ...


    class azure.mgmt.securityinsight.aio.operations.GetTriggeredAnalyticsRuleRunsOperations:

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
                **kwargs: Any
            ) -> AsyncItemPaged[TriggeredAnalyticsRuleRun]: ...


    class azure.mgmt.securityinsight.aio.operations.HuntCommentsOperations:

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
                hunt_id: str, 
                hunt_comment_id: str, 
                hunt_comment: HuntComment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntComment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_comment_id: str, 
                hunt_comment: HuntComment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntComment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_comment_id: str, 
                hunt_comment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntComment: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'hunt_comment_id']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_comment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'hunt_comment_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_comment_id: str, 
                **kwargs: Any
            ) -> HuntComment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'filter', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[HuntComment]: ...


    class azure.mgmt.securityinsight.aio.operations.HuntRelationsOperations:

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
                hunt_id: str, 
                hunt_relation_id: str, 
                hunt_relation: HuntRelation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntRelation: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_relation_id: str, 
                hunt_relation: HuntRelation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntRelation: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_relation_id: str, 
                hunt_relation: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntRelation: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'hunt_relation_id']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_relation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'hunt_relation_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_relation_id: str, 
                **kwargs: Any
            ) -> HuntRelation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'filter', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[HuntRelation]: ...


    class azure.mgmt.securityinsight.aio.operations.HuntsOperations:

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
                hunt_id: str, 
                hunt: Hunt, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Hunt: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt: Hunt, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Hunt: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Hunt: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                **kwargs: Any
            ) -> Hunt: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'filter', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Hunt]: ...


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
                incident_comment: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_comment_id: str, 
                **kwargs: Any
            ) -> IncidentComment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[IncidentComment]: ...


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
                relation: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                relation_name: str, 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Relation]: ...


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
                incident_task: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_task_id: str, 
                **kwargs: Any
            ) -> IncidentTask: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IncidentTask]: ...


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
                incident: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Incident: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                **kwargs: Any
            ) -> Incident: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Incident]: ...

        @distributed_trace_async
        async def list_alerts(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                **kwargs: Any
            ) -> IncidentAlertList: ...

        @distributed_trace_async
        async def list_bookmarks(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                **kwargs: Any
            ) -> IncidentBookmarkList: ...

        @distributed_trace_async
        async def list_entities(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
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
            ) -> Any: ...

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
            ) -> Any: ...

        @overload
        async def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_identifier: str, 
                request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...


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
                metadata: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                **kwargs: Any
            ) -> MetadataModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MetadataModel]: ...

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
                metadata_patch: IO[bytes], 
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
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'consent_id']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                consent_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'consent_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                consent_id: str, 
                **kwargs: Any
            ) -> OfficeConsent: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OfficeConsent]: ...


    class azure.mgmt.securityinsight.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.securityinsight.aio.operations.ProductPackageOperations:

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
                package_id: str, 
                **kwargs: Any
            ) -> ProductPackageModel: ...


    class azure.mgmt.securityinsight.aio.operations.ProductPackagesOperations:

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
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProductPackageModel]: ...


    class azure.mgmt.securityinsight.aio.operations.ProductSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'settings_name']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'settings_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                **kwargs: Any
            ) -> Settings: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Settings]: ...

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
                settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...


    class azure.mgmt.securityinsight.aio.operations.ProductTemplateOperations:

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
                template_id: str, 
                **kwargs: Any
            ) -> ProductTemplateModel: ...


    class azure.mgmt.securityinsight.aio.operations.ProductTemplatesOperations:

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
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProductTemplateModel]: ...


    class azure.mgmt.securityinsight.aio.operations.ReevaluateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                **kwargs: Any
            ) -> ReevaluateResponse: ...


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
                security_ml_analytics_setting: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_resource_name: str, 
                **kwargs: Any
            ) -> SecurityMLAnalyticsSetting: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityMLAnalyticsSetting]: ...


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
                sentinel_onboarding_state_parameter: Optional[IO[bytes]] = None, 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sentinel_onboarding_state_name: str, 
                **kwargs: Any
            ) -> SentinelOnboardingState: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> SentinelOnboardingStatesList: ...


    class azure.mgmt.securityinsight.aio.operations.SourceControlOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list_repositories(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                repository_access: RepositoryAccessProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[Repo]: ...

        @overload
        def list_repositories(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                repository_access: RepositoryAccessProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[Repo]: ...

        @overload
        def list_repositories(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                repository_access: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[Repo]: ...


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
                source_control: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @overload
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                repository_access: RepositoryAccessProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Warning: ...

        @overload
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                repository_access: RepositoryAccessProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Warning: ...

        @overload
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                repository_access: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Warning: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SourceControl]: ...


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
                threat_intelligence_append_tags: IO[bytes], 
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
                threat_intelligence_properties: IO[bytes], 
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
                threat_intelligence_properties: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
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
            ) -> AsyncItemPaged[ThreatIntelligenceInformation]: ...

        @overload
        def query_indicators(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_filtering_criteria: ThreatIntelligenceFilteringCriteria, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[ThreatIntelligenceInformation]: ...

        @overload
        def query_indicators(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_filtering_criteria: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[ThreatIntelligenceInformation]: ...

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
                threat_intelligence_replace_tags: IO[bytes], 
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
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ThreatIntelligenceInformation]: ...


    class azure.mgmt.securityinsight.aio.operations.ThreatIntelligenceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def count(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[CountQuery] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceCount: ...

        @overload
        async def count(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[CountQuery] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceCount: ...

        @overload
        async def count(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceCount: ...

        @overload
        def query(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[Query] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[TIObject]: ...

        @overload
        def query(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[Query] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[TIObject]: ...

        @overload
        def query(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[TIObject]: ...


    class azure.mgmt.securityinsight.aio.operations.TriggeredAnalyticsRuleRunOperations:

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
                rule_run_id: str, 
                **kwargs: Any
            ) -> TriggeredAnalyticsRuleRun: ...


    class azure.mgmt.securityinsight.aio.operations.UpdateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                recommendation_patch: RecommendationPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Recommendation: ...

        @overload
        async def recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                recommendation_patch: RecommendationPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Recommendation: ...

        @overload
        async def recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                recommendation_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Recommendation: ...


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
                watchlist_item: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist_item_id: str, 
                **kwargs: Any
            ) -> WatchlistItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[WatchlistItem]: ...


    class azure.mgmt.securityinsight.aio.operations.WatchlistsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist: Watchlist, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Watchlist]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist: Watchlist, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Watchlist]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Watchlist]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Watchlist]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                **kwargs: Any
            ) -> Watchlist: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Watchlist]: ...


    class azure.mgmt.securityinsight.aio.operations.WorkspaceManagerAssignmentJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                *, 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Job]: ...


    class azure.mgmt.securityinsight.aio.operations.WorkspaceManagerAssignmentsOperations:

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
                workspace_manager_assignment_name: str, 
                workspace_manager_assignment: WorkspaceManagerAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerAssignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                workspace_manager_assignment: WorkspaceManagerAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerAssignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                workspace_manager_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerAssignment: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_assignment_name']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_assignment_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                **kwargs: Any
            ) -> WorkspaceManagerAssignment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkspaceManagerAssignment]: ...


    class azure.mgmt.securityinsight.aio.operations.WorkspaceManagerConfigurationsOperations:

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
                workspace_manager_configuration_name: str, 
                workspace_manager_configuration: WorkspaceManagerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_configuration_name: str, 
                workspace_manager_configuration: WorkspaceManagerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_configuration_name: str, 
                workspace_manager_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerConfiguration: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_configuration_name']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_configuration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_configuration_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_configuration_name: str, 
                **kwargs: Any
            ) -> WorkspaceManagerConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkspaceManagerConfiguration]: ...


    class azure.mgmt.securityinsight.aio.operations.WorkspaceManagerGroupsOperations:

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
                workspace_manager_group_name: str, 
                workspace_manager_group: WorkspaceManagerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_group_name: str, 
                workspace_manager_group: WorkspaceManagerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_group_name: str, 
                workspace_manager_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerGroup: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_group_name']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_group_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_group_name: str, 
                **kwargs: Any
            ) -> WorkspaceManagerGroup: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkspaceManagerGroup]: ...


    class azure.mgmt.securityinsight.aio.operations.WorkspaceManagerMembersOperations:

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
                workspace_manager_member_name: str, 
                workspace_manager_member: WorkspaceManagerMember, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerMember: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_member_name: str, 
                workspace_manager_member: WorkspaceManagerMember, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerMember: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_member_name: str, 
                workspace_manager_member: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerMember: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_member_name']}, api_versions_list=['2025-10-01-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_member_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_member_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_member_name: str, 
                **kwargs: Any
            ) -> WorkspaceManagerMember: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkspaceManagerMember]: ...


namespace azure.mgmt.securityinsight.models

    class azure.mgmt.securityinsight.models.AADCheckRequirements(DataConnectorsCheckRequirements, discriminator='AzureActiveDirectory'):
        kind: Literal[DataConnectorKind.AZURE_ACTIVE_DIRECTORY]
        properties: Optional[AADCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AADCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AADCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AADDataConnector(DataConnector, discriminator='AzureActiveDirectory'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.AZURE_ACTIVE_DIRECTORY]
        name: str
        properties: Optional[AADDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[AADDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AADDataConnectorProperties(_Model):
        data_types: Optional[AlertsDataTypeOfDataConnector]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AATPCheckRequirements(DataConnectorsCheckRequirements, discriminator='AzureAdvancedThreatProtection'):
        kind: Literal[DataConnectorKind.AZURE_ADVANCED_THREAT_PROTECTION]
        properties: Optional[AATPCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AATPCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AATPCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AATPDataConnector(DataConnector, discriminator='AzureAdvancedThreatProtection'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.AZURE_ADVANCED_THREAT_PROTECTION]
        name: str
        properties: Optional[AATPDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[AATPDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AATPDataConnectorProperties(_Model):
        data_types: Optional[AlertsDataTypeOfDataConnector]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ASCCheckRequirements(DataConnectorsCheckRequirements, discriminator='AzureSecurityCenter'):
        kind: Literal[DataConnectorKind.AZURE_SECURITY_CENTER]
        properties: Optional[ASCCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ASCCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ASCCheckRequirementsProperties(_Model):
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ASCDataConnector(DataConnector, discriminator='AzureSecurityCenter'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.AZURE_SECURITY_CENTER]
        name: str
        properties: Optional[ASCDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ASCDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ASCDataConnectorProperties(DataConnectorWithAlertsProperties):
        data_types: AlertsDataTypeOfDataConnector
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AWSAuthModel(CcpAuthConfig, discriminator='AWS'):
        external_id: Optional[str]
        role_arn: str
        type: Literal[CcpAuthType.AWS]

        @overload
        def __init__(
                self, 
                *, 
                external_id: Optional[str] = ..., 
                role_arn: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AccountEntity(Entity, discriminator='Account'):
        id: str
        kind: Literal[EntityKind.ACCOUNT]
        name: str
        properties: Optional[AccountEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccountEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AccountEntityProperties(EntityCommonProperties):
        aad_tenant_id: Optional[str]
        aad_user_id: Optional[str]
        account_name: Optional[str]
        additional_data: dict[str, any]
        display_name: Optional[str]
        dns_domain: Optional[str]
        friendly_name: str
        host_entity_id: Optional[str]
        is_domain_joined: Optional[bool]
        nt_domain: Optional[str]
        object_guid: Optional[str]
        puid: Optional[str]
        sid: Optional[str]
        upn_suffix: Optional[str]


    class azure.mgmt.securityinsight.models.ActionPropertiesBase(_Model):
        logic_app_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                logic_app_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ActionRequest(ResourceWithEtag):
        etag: str
        id: str
        name: str
        properties: Optional[ActionRequestProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ActionRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ActionRequestProperties(ActionPropertiesBase):
        logic_app_resource_id: str
        trigger_uri: str

        @overload
        def __init__(
                self, 
                *, 
                logic_app_resource_id: str, 
                trigger_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ActionResponse(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[ActionResponseProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ActionResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ActionResponseProperties(ActionPropertiesBase):
        logic_app_resource_id: str
        workflow_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                logic_app_resource_id: str, 
                workflow_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_INCIDENT_TASK = "AddIncidentTask"
        MODIFY_PROPERTIES = "ModifyProperties"
        RUN_PLAYBOOK = "RunPlaybook"


    class azure.mgmt.securityinsight.models.ActivityCustomEntityQuery(CustomEntityQuery, discriminator='Activity'):
        etag: str
        id: str
        kind: Literal[CustomEntityQueryKind.ACTIVITY]
        name: str
        properties: Optional[ActivityEntityQueriesProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ActivityEntityQueriesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ActivityEntityQueriesProperties(_Model):
        content: Optional[str]
        created_time_utc: Optional[datetime]
        description: Optional[str]
        enabled: Optional[bool]
        entities_filter: Optional[dict[str, list[str]]]
        input_entity_type: Optional[Union[str, EntityType]]
        last_modified_time_utc: Optional[datetime]
        query_definitions: Optional[ActivityEntityQueriesPropertiesQueryDefinitions]
        required_input_fields_sets: Optional[list[list[str]]]
        template_name: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                entities_filter: Optional[dict[str, list[str]]] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                query_definitions: Optional[ActivityEntityQueriesPropertiesQueryDefinitions] = ..., 
                required_input_fields_sets: Optional[list[list[str]]] = ..., 
                template_name: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ActivityEntityQueriesPropertiesQueryDefinitions(_Model):
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ActivityEntityQuery(EntityQuery, discriminator='Activity'):
        etag: str
        id: str
        kind: Literal[EntityQueryKind.ACTIVITY]
        name: str
        properties: Optional[ActivityEntityQueriesProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ActivityEntityQueriesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ActivityEntityQueryTemplate(EntityQueryTemplate, discriminator='Activity'):
        id: str
        kind: Literal[EntityQueryTemplateKind.ACTIVITY]
        name: str
        properties: Optional[ActivityEntityQueryTemplateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ActivityEntityQueryTemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ActivityEntityQueryTemplateProperties(_Model):
        content: Optional[str]
        data_types: Optional[list[DataTypeDefinitions]]
        description: Optional[str]
        entities_filter: Optional[dict[str, list[str]]]
        input_entity_type: Optional[Union[str, EntityType]]
        query_definitions: Optional[ActivityEntityQueryTemplatePropertiesQueryDefinitions]
        required_input_fields_sets: Optional[list[list[str]]]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                data_types: Optional[list[DataTypeDefinitions]] = ..., 
                description: Optional[str] = ..., 
                entities_filter: Optional[dict[str, list[str]]] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                query_definitions: Optional[ActivityEntityQueryTemplatePropertiesQueryDefinitions] = ..., 
                required_input_fields_sets: Optional[list[list[str]]] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ActivityEntityQueryTemplatePropertiesQueryDefinitions(_Model):
        query: Optional[str]
        summarize_by: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                query: Optional[str] = ..., 
                summarize_by: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ActivityTimelineItem(EntityTimelineItem, discriminator='Activity'):
        bucket_end_time_utc: datetime
        bucket_start_time_utc: datetime
        content: str
        first_activity_time_utc: datetime
        kind: Literal[EntityTimelineKind.ACTIVITY]
        last_activity_time_utc: datetime
        query_id: str
        title: str

        @overload
        def __init__(
                self, 
                *, 
                bucket_end_time_utc: datetime, 
                bucket_start_time_utc: datetime, 
                content: str, 
                first_activity_time_utc: datetime, 
                last_activity_time_utc: datetime, 
                query_id: str, 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AddIncidentTaskActionProperties(_Model):
        description: Optional[str]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AlertDetail(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISPLAY_NAME = "DisplayName"
        SEVERITY = "Severity"


    class azure.mgmt.securityinsight.models.AlertDetailsOverride(_Model):
        alert_description_format: Optional[str]
        alert_display_name_format: Optional[str]
        alert_dynamic_properties: Optional[list[AlertPropertyMapping]]
        alert_severity_column_name: Optional[str]
        alert_tactics_column_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                alert_description_format: Optional[str] = ..., 
                alert_display_name_format: Optional[str] = ..., 
                alert_dynamic_properties: Optional[list[AlertPropertyMapping]] = ..., 
                alert_severity_column_name: Optional[str] = ..., 
                alert_tactics_column_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AlertProperty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_LINK = "AlertLink"
        CONFIDENCE_LEVEL = "ConfidenceLevel"
        CONFIDENCE_SCORE = "ConfidenceScore"
        EXTENDED_LINKS = "ExtendedLinks"
        PRODUCT_COMPONENT_NAME = "ProductComponentName"
        PRODUCT_NAME = "ProductName"
        PROVIDER_NAME = "ProviderName"
        REMEDIATION_STEPS = "RemediationSteps"
        SUB_TECHNIQUES = "SubTechniques"
        TECHNIQUES = "Techniques"


    class azure.mgmt.securityinsight.models.AlertPropertyMapping(_Model):
        alert_property: Optional[Union[str, AlertProperty]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                alert_property: Optional[Union[str, AlertProperty]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AlertRule(ProxyResource):
        etag: Optional[str]
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AlertRuleKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUSION = "Fusion"
        MICROSOFT_SECURITY_INCIDENT_CREATION = "MicrosoftSecurityIncidentCreation"
        ML_BEHAVIOR_ANALYTICS = "MLBehaviorAnalytics"
        NRT = "NRT"
        SCHEDULED = "Scheduled"
        THREAT_INTELLIGENCE = "ThreatIntelligence"


    class azure.mgmt.securityinsight.models.AlertRuleTemplate(ProxyResource):
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AlertRuleTemplateDataSource(_Model):
        connector_id: Optional[str]
        data_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                connector_id: Optional[str] = ..., 
                data_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AlertRuleTemplatePropertiesBase(_Model):
        alert_rules_created_by_template_count: Optional[int]
        created_date_utc: Optional[datetime]
        description: Optional[str]
        display_name: Optional[str]
        last_updated_date_utc: Optional[datetime]
        required_data_connectors: Optional[list[AlertRuleTemplateDataSource]]
        status: Optional[Union[str, TemplateStatus]]

        @overload
        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[list[AlertRuleTemplateDataSource]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AlertRuleTemplateWithMitreProperties(AlertRuleTemplatePropertiesBase):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        last_updated_date_utc: datetime
        required_data_connectors: list[AlertRuleTemplateDataSource]
        status: Union[str, TemplateStatus]
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[list[AlertRuleTemplateDataSource]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.securityinsight.models.AlertsDataTypeOfDataConnector(_Model):
        alerts: DataConnectorDataTypeCommon

        @overload
        def __init__(
                self, 
                *, 
                alerts: DataConnectorDataTypeCommon
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AnalyticsRuleRunTrigger(_Model):
        properties: AnalyticsRuleRunTriggerProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: AnalyticsRuleRunTriggerProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AnalyticsRuleRunTriggerProperties(_Model):
        execution_time_utc: datetime

        @overload
        def __init__(
                self, 
                *, 
                execution_time_utc: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Anomalies(Settings, discriminator='Anomalies'):
        etag: str
        id: str
        kind: Literal[SettingKind.ANOMALIES]
        name: str
        properties: Optional[AnomaliesSettingsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[AnomaliesSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AnomaliesSettingsProperties(_Model):
        is_enabled: Optional[bool]


    class azure.mgmt.securityinsight.models.AnomalySecurityMLAnalyticsSettings(SecurityMLAnalyticsSetting, discriminator='Anomaly'):
        etag: str
        id: str
        kind: Literal[SecurityMLAnalyticsSettingsKind.ANOMALY]
        name: str
        properties: Optional[AnomalySecurityMLAnalyticsSettingsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[AnomalySecurityMLAnalyticsSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AnomalySecurityMLAnalyticsSettingsProperties(_Model):
        anomaly_settings_version: Optional[int]
        anomaly_version: str
        customizable_observations: Optional[Any]
        description: Optional[str]
        display_name: str
        enabled: bool
        frequency: timedelta
        is_default_settings: bool
        last_modified_utc: Optional[datetime]
        required_data_connectors: Optional[list[SecurityMLAnalyticsSettingsDataSource]]
        settings_definition_id: Optional[str]
        settings_status: Union[str, SettingsStatus]
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                anomaly_settings_version: Optional[int] = ..., 
                anomaly_version: str, 
                customizable_observations: Optional[Any] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                enabled: bool, 
                frequency: timedelta, 
                is_default_settings: bool, 
                required_data_connectors: Optional[list[SecurityMLAnalyticsSettingsDataSource]] = ..., 
                settings_definition_id: Optional[str] = ..., 
                settings_status: Union[str, SettingsStatus], 
                tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AnomalyTimelineItem(EntityTimelineItem, discriminator='Anomaly'):
        azure_resource_id: str
        description: Optional[str]
        display_name: str
        end_time_utc: datetime
        intent: Optional[str]
        kind: Literal[EntityTimelineKind.ANOMALY]
        product_name: Optional[str]
        reasons: Optional[list[str]]
        start_time_utc: datetime
        techniques: Optional[list[str]]
        time_generated: datetime
        vendor: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_id: str, 
                description: Optional[str] = ..., 
                display_name: str, 
                end_time_utc: datetime, 
                intent: Optional[str] = ..., 
                product_name: Optional[str] = ..., 
                reasons: Optional[list[str]] = ..., 
                start_time_utc: datetime, 
                techniques: Optional[list[str]] = ..., 
                time_generated: datetime, 
                vendor: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AntispamMailDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        INTRAORG = "Intraorg"
        OUTBOUND = "Outbound"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.ApiKeyAuthModel(CcpAuthConfig, discriminator='APIKey'):
        api_key: str
        api_key_identifier: Optional[str]
        api_key_name: str
        is_api_key_in_post_payload: Optional[bool]
        type: Literal[CcpAuthType.API_KEY]

        @overload
        def __init__(
                self, 
                *, 
                api_key: str, 
                api_key_identifier: Optional[str] = ..., 
                api_key_name: str, 
                is_api_key_in_post_payload: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ApiPollingParameters(_Model):
        connector_ui_config: Optional[CodelessUiConnectorConfigProperties]
        polling_config: Optional[CodelessConnectorPollingConfigProperties]

        @overload
        def __init__(
                self, 
                *, 
                connector_ui_config: Optional[CodelessUiConnectorConfigProperties] = ..., 
                polling_config: Optional[CodelessConnectorPollingConfigProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AssignmentItem(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AttackPattern(TIObject, discriminator='AttackPattern'):
        id: str
        kind: Literal[TIObjectKind.ATTACK_PATTERN]
        name: str
        properties: TIObjectCommonProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TIObjectCommonProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


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


    class azure.mgmt.securityinsight.models.AutomationRule(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: AutomationRuleProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: AutomationRuleProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRuleAction(_Model):
        action_type: str
        order: int

        @overload
        def __init__(
                self, 
                *, 
                action_type: str, 
                order: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRuleAddIncidentTaskAction(AutomationRuleAction, discriminator='AddIncidentTask'):
        action_configuration: Optional[AddIncidentTaskActionProperties]
        action_type: Literal[ActionType.ADD_INCIDENT_TASK]
        order: int

        @overload
        def __init__(
                self, 
                *, 
                action_configuration: Optional[AddIncidentTaskActionProperties] = ..., 
                order: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRuleBooleanCondition(_Model):
        inner_conditions: Optional[list[AutomationRuleCondition]]
        operator: Optional[Union[str, AutomationRuleBooleanConditionSupportedOperator]]

        @overload
        def __init__(
                self, 
                *, 
                inner_conditions: Optional[list[AutomationRuleCondition]] = ..., 
                operator: Optional[Union[str, AutomationRuleBooleanConditionSupportedOperator]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRuleBooleanConditionSupportedOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AND = "And"
        OR = "Or"


    class azure.mgmt.securityinsight.models.AutomationRuleCondition(_Model):
        condition_type: str

        @overload
        def __init__(
                self, 
                *, 
                condition_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRuleModifyPropertiesAction(AutomationRuleAction, discriminator='ModifyProperties'):
        action_configuration: Optional[IncidentPropertiesAction]
        action_type: Literal[ActionType.MODIFY_PROPERTIES]
        order: int

        @overload
        def __init__(
                self, 
                *, 
                action_configuration: Optional[IncidentPropertiesAction] = ..., 
                order: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRuleProperties(_Model):
        actions: list[AutomationRuleAction]
        created_by: Optional[ClientInfo]
        created_time_utc: Optional[datetime]
        display_name: str
        last_modified_by: Optional[ClientInfo]
        last_modified_time_utc: Optional[datetime]
        order: int
        triggering_logic: AutomationRuleTriggeringLogic

        @overload
        def __init__(
                self, 
                *, 
                actions: list[AutomationRuleAction], 
                display_name: str, 
                order: int, 
                triggering_logic: AutomationRuleTriggeringLogic
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayChangedConditionSupportedArrayType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"
        COMMENTS = "Comments"
        LABELS = "Labels"
        TACTICS = "Tactics"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayChangedConditionSupportedChangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDED = "Added"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayChangedValuesCondition(_Model):
        array_type: Optional[Union[str, AutomationRulePropertyArrayChangedConditionSupportedArrayType]]
        change_type: Optional[Union[str, AutomationRulePropertyArrayChangedConditionSupportedChangeType]]

        @overload
        def __init__(
                self, 
                *, 
                array_type: Optional[Union[str, AutomationRulePropertyArrayChangedConditionSupportedArrayType]] = ..., 
                change_type: Optional[Union[str, AutomationRulePropertyArrayChangedConditionSupportedChangeType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayConditionSupportedArrayConditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_ITEMS = "AllItems"
        ANY_ITEM = "AnyItem"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayConditionSupportedArrayType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_DETAILS = "CustomDetails"
        CUSTOM_DETAIL_VALUES = "CustomDetailValues"
        INCIDENT_LABELS = "IncidentLabels"


    class azure.mgmt.securityinsight.models.AutomationRulePropertyArrayValuesCondition(_Model):
        array_condition_type: Optional[Union[str, AutomationRulePropertyArrayConditionSupportedArrayConditionType]]
        array_type: Optional[Union[str, AutomationRulePropertyArrayConditionSupportedArrayType]]
        item_conditions: Optional[list[AutomationRuleCondition]]

        @overload
        def __init__(
                self, 
                *, 
                array_condition_type: Optional[Union[str, AutomationRulePropertyArrayConditionSupportedArrayConditionType]] = ..., 
                array_type: Optional[Union[str, AutomationRulePropertyArrayConditionSupportedArrayType]] = ..., 
                item_conditions: Optional[list[AutomationRuleCondition]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        INCIDENT_ALERT_TITLE = "IncidentAlertTitle"
        INCIDENT_CUSTOM_DETAILS_KEY = "IncidentCustomDetailsKey"
        INCIDENT_CUSTOM_DETAILS_VALUE = "IncidentCustomDetailsValue"
        INCIDENT_CUSTOM_DETECTION_RULE_IDS = "IncidentCustomDetectionRuleIds"
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


    class azure.mgmt.securityinsight.models.AutomationRulePropertyValuesChangedCondition(_Model):
        change_type: Optional[Union[str, AutomationRulePropertyChangedConditionSupportedChangedType]]
        operator: Optional[Union[str, AutomationRulePropertyConditionSupportedOperator]]
        property_name: Optional[Union[str, AutomationRulePropertyChangedConditionSupportedPropertyType]]
        property_values: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                change_type: Optional[Union[str, AutomationRulePropertyChangedConditionSupportedChangedType]] = ..., 
                operator: Optional[Union[str, AutomationRulePropertyConditionSupportedOperator]] = ..., 
                property_name: Optional[Union[str, AutomationRulePropertyChangedConditionSupportedPropertyType]] = ..., 
                property_values: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRulePropertyValuesCondition(_Model):
        operator: Optional[Union[str, AutomationRulePropertyConditionSupportedOperator]]
        property_name: Optional[Union[str, AutomationRulePropertyConditionSupportedProperty]]
        property_values: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                operator: Optional[Union[str, AutomationRulePropertyConditionSupportedOperator]] = ..., 
                property_name: Optional[Union[str, AutomationRulePropertyConditionSupportedProperty]] = ..., 
                property_values: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRuleRunPlaybookAction(AutomationRuleAction, discriminator='RunPlaybook'):
        action_configuration: Optional[PlaybookActionProperties]
        action_type: Literal[ActionType.RUN_PLAYBOOK]
        order: int

        @overload
        def __init__(
                self, 
                *, 
                action_configuration: Optional[PlaybookActionProperties] = ..., 
                order: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AutomationRuleTriggeringLogic(_Model):
        conditions: Optional[list[AutomationRuleCondition]]
        expiration_time_utc: Optional[datetime]
        is_enabled: bool
        triggers_on: Union[str, TriggersOn]
        triggers_when: Union[str, TriggersWhen]

        @overload
        def __init__(
                self, 
                *, 
                conditions: Optional[list[AutomationRuleCondition]] = ..., 
                expiration_time_utc: Optional[datetime] = ..., 
                is_enabled: bool, 
                triggers_on: Union[str, TriggersOn], 
                triggers_when: Union[str, TriggersWhen]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Availability(_Model):
        is_preview: Optional[bool]
        status: Optional[Literal[1]]

        @overload
        def __init__(
                self, 
                *, 
                is_preview: Optional[bool] = ..., 
                status: Optional[Literal[1]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AwsCloudTrailCheckRequirements(DataConnectorsCheckRequirements, discriminator='AmazonWebServicesCloudTrail'):
        kind: Literal[DataConnectorKind.AMAZON_WEB_SERVICES_CLOUD_TRAIL]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AwsCloudTrailDataConnector(DataConnector, discriminator='AmazonWebServicesCloudTrail'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.AMAZON_WEB_SERVICES_CLOUD_TRAIL]
        name: str
        properties: Optional[AwsCloudTrailDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[AwsCloudTrailDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AwsCloudTrailDataConnectorDataTypes(_Model):
        logs: AwsCloudTrailDataConnectorDataTypesLogs

        @overload
        def __init__(
                self, 
                *, 
                logs: AwsCloudTrailDataConnectorDataTypesLogs
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AwsCloudTrailDataConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AwsCloudTrailDataConnectorProperties(_Model):
        aws_role_arn: Optional[str]
        data_types: AwsCloudTrailDataConnectorDataTypes

        @overload
        def __init__(
                self, 
                *, 
                aws_role_arn: Optional[str] = ..., 
                data_types: AwsCloudTrailDataConnectorDataTypes
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AwsS3CheckRequirements(DataConnectorsCheckRequirements, discriminator='AmazonWebServicesS3'):
        kind: Literal[DataConnectorKind.AMAZON_WEB_SERVICES_S3]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AwsS3DataConnector(DataConnector, discriminator='AmazonWebServicesS3'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.AMAZON_WEB_SERVICES_S3]
        name: str
        properties: Optional[AwsS3DataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[AwsS3DataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AwsS3DataConnectorDataTypes(_Model):
        logs: AwsS3DataConnectorDataTypesLogs

        @overload
        def __init__(
                self, 
                *, 
                logs: AwsS3DataConnectorDataTypesLogs
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AwsS3DataConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AwsS3DataConnectorProperties(_Model):
        data_types: AwsS3DataConnectorDataTypes
        destination_table: str
        role_arn: str
        sqs_urls: list[str]

        @overload
        def __init__(
                self, 
                *, 
                data_types: AwsS3DataConnectorDataTypes, 
                destination_table: str, 
                role_arn: str, 
                sqs_urls: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AzureDevOpsResourceInfo(_Model):
        pipeline_id: Optional[str]
        service_connection_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                pipeline_id: Optional[str] = ..., 
                service_connection_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.AzureResourceEntity(Entity, discriminator='AzureResource'):
        id: str
        kind: Literal[EntityKind.AZURE_RESOURCE]
        name: str
        properties: Optional[AzureResourceEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureResourceEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.AzureResourceEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        resource_id: Optional[str]
        subscription_id: Optional[str]


    class azure.mgmt.securityinsight.models.BasicAuthModel(CcpAuthConfig, discriminator='Basic'):
        password: str
        type: Literal[CcpAuthType.BASIC]
        user_name: str

        @overload
        def __init__(
                self, 
                *, 
                password: str, 
                user_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.BillingStatistic(ProxyResource):
        etag: Optional[str]
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.BillingStatisticKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SAP_SOLUTION_USAGE = "SapSolutionUsage"


    class azure.mgmt.securityinsight.models.Bookmark(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[BookmarkProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[BookmarkProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.BookmarkEntityMappings(_Model):
        entity_type: Optional[str]
        field_mappings: Optional[list[EntityFieldMapping]]

        @overload
        def __init__(
                self, 
                *, 
                entity_type: Optional[str] = ..., 
                field_mappings: Optional[list[EntityFieldMapping]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.BookmarkExpandParameters(_Model):
        end_time: Optional[datetime]
        expansion_id: Optional[str]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                expansion_id: Optional[str] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.BookmarkExpandResponse(_Model):
        meta_data: Optional[ExpansionResultsMetadata]
        value: Optional[BookmarkExpandResponseValue]

        @overload
        def __init__(
                self, 
                *, 
                meta_data: Optional[ExpansionResultsMetadata] = ..., 
                value: Optional[BookmarkExpandResponseValue] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.BookmarkExpandResponseValue(_Model):
        edges: Optional[list[ConnectedEntity]]
        entities: Optional[list[Entity]]

        @overload
        def __init__(
                self, 
                *, 
                edges: Optional[list[ConnectedEntity]] = ..., 
                entities: Optional[list[Entity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.BookmarkProperties(_Model):
        created: Optional[datetime]
        created_by: Optional[UserInfo]
        display_name: str
        entity_mappings: Optional[list[BookmarkEntityMappings]]
        event_time: Optional[datetime]
        incident_info: Optional[IncidentInfo]
        labels: Optional[list[str]]
        notes: Optional[str]
        query: str
        query_end_time: Optional[datetime]
        query_result: Optional[str]
        query_start_time: Optional[datetime]
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]
        updated: Optional[datetime]
        updated_by: Optional[UserInfo]

        @overload
        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                created_by: Optional[UserInfo] = ..., 
                display_name: str, 
                entity_mappings: Optional[list[BookmarkEntityMappings]] = ..., 
                event_time: Optional[datetime] = ..., 
                incident_info: Optional[IncidentInfo] = ..., 
                labels: Optional[list[str]] = ..., 
                notes: Optional[str] = ..., 
                query: str, 
                query_end_time: Optional[datetime] = ..., 
                query_result: Optional[str] = ..., 
                query_start_time: Optional[datetime] = ..., 
                tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[list[str]] = ..., 
                updated: Optional[datetime] = ..., 
                updated_by: Optional[UserInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.BookmarkTimelineItem(EntityTimelineItem, discriminator='Bookmark'):
        azure_resource_id: str
        created_by: Optional[UserInfo]
        display_name: Optional[str]
        end_time_utc: Optional[datetime]
        event_time: Optional[datetime]
        kind: Literal[EntityTimelineKind.BOOKMARK]
        labels: Optional[list[str]]
        notes: Optional[str]
        start_time_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_id: str, 
                created_by: Optional[UserInfo] = ..., 
                display_name: Optional[str] = ..., 
                end_time_utc: Optional[datetime] = ..., 
                event_time: Optional[datetime] = ..., 
                labels: Optional[list[str]] = ..., 
                notes: Optional[str] = ..., 
                start_time_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.BooleanConditionProperties(AutomationRuleCondition, discriminator='Boolean'):
        condition_properties: Optional[AutomationRuleBooleanCondition]
        condition_type: Literal[ConditionType.BOOLEAN]

        @overload
        def __init__(
                self, 
                *, 
                condition_properties: Optional[AutomationRuleBooleanCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CcpAuthConfig(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CcpAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        API_KEY = "APIKey"
        AWS = "AWS"
        BASIC = "Basic"
        GCP = "GCP"
        GIT_HUB = "GitHub"
        JWT_TOKEN = "JwtToken"
        NONE = "None"
        ORACLE = "Oracle"
        O_AUTH2 = "OAuth2"
        SERVICE_BUS = "ServiceBus"
        SESSION = "Session"


    class azure.mgmt.securityinsight.models.CcpResponseConfig(_Model):
        compression_algo: Optional[str]
        convert_child_properties_to_array: Optional[bool]
        csv_delimiter: Optional[str]
        csv_escape: Optional[str]
        events_json_paths: list[str]
        format: Optional[str]
        has_csv_boundary: Optional[bool]
        has_csv_header: Optional[bool]
        is_gzip_compressed: Optional[bool]
        success_status_json_path: Optional[str]
        success_status_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                compression_algo: Optional[str] = ..., 
                convert_child_properties_to_array: Optional[bool] = ..., 
                csv_delimiter: Optional[str] = ..., 
                csv_escape: Optional[str] = ..., 
                events_json_paths: list[str], 
                format: Optional[str] = ..., 
                has_csv_boundary: Optional[bool] = ..., 
                has_csv_header: Optional[bool] = ..., 
                is_gzip_compressed: Optional[bool] = ..., 
                success_status_json_path: Optional[str] = ..., 
                success_status_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ClientInfo(_Model):
        email: Optional[str]
        name: Optional[str]
        object_id: Optional[str]
        user_principal_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                name: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                user_principal_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CloudApplicationEntity(Entity, discriminator='CloudApplication'):
        id: str
        kind: Literal[EntityKind.CLOUD_APPLICATION]
        name: str
        properties: Optional[CloudApplicationEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudApplicationEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.CloudApplicationEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        app_id: Optional[int]
        app_name: Optional[str]
        friendly_name: str
        instance_name: Optional[str]


    class azure.mgmt.securityinsight.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CloudErrorBody(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.securityinsight.models.CodelessApiPollingDataConnector(DataConnector, discriminator='APIPolling'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.API_POLLING]
        name: str
        properties: Optional[ApiPollingParameters]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ApiPollingParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessConnectorPollingAuthProperties(_Model):
        api_key_identifier: Optional[str]
        api_key_name: Optional[str]
        auth_type: str
        authorization_endpoint: Optional[str]
        authorization_endpoint_query_parameters: Optional[Any]
        flow_name: Optional[str]
        is_api_key_in_post_payload: Optional[str]
        is_client_secret_in_header: Optional[bool]
        redirection_endpoint: Optional[str]
        scope: Optional[str]
        token_endpoint: Optional[str]
        token_endpoint_headers: Optional[Any]
        token_endpoint_query_parameters: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                api_key_identifier: Optional[str] = ..., 
                api_key_name: Optional[str] = ..., 
                auth_type: str, 
                authorization_endpoint: Optional[str] = ..., 
                authorization_endpoint_query_parameters: Optional[Any] = ..., 
                flow_name: Optional[str] = ..., 
                is_api_key_in_post_payload: Optional[str] = ..., 
                is_client_secret_in_header: Optional[bool] = ..., 
                redirection_endpoint: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                token_endpoint: Optional[str] = ..., 
                token_endpoint_headers: Optional[Any] = ..., 
                token_endpoint_query_parameters: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessConnectorPollingConfigProperties(_Model):
        auth: CodelessConnectorPollingAuthProperties
        is_active: Optional[bool]
        paging: Optional[CodelessConnectorPollingPagingProperties]
        request: CodelessConnectorPollingRequestProperties
        response: Optional[CodelessConnectorPollingResponseProperties]

        @overload
        def __init__(
                self, 
                *, 
                auth: CodelessConnectorPollingAuthProperties, 
                is_active: Optional[bool] = ..., 
                paging: Optional[CodelessConnectorPollingPagingProperties] = ..., 
                request: CodelessConnectorPollingRequestProperties, 
                response: Optional[CodelessConnectorPollingResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessConnectorPollingPagingProperties(_Model):
        next_page_para_name: Optional[str]
        next_page_token_json_path: Optional[str]
        page_count_attribute_path: Optional[str]
        page_size: Optional[int]
        page_size_para_name: Optional[str]
        page_time_stamp_attribute_path: Optional[str]
        page_total_count_attribute_path: Optional[str]
        paging_type: str
        search_the_latest_time_stamp_from_events_list: Optional[str]

        @overload
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
                search_the_latest_time_stamp_from_events_list: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessConnectorPollingRequestProperties(_Model):
        api_endpoint: str
        end_time_attribute_name: Optional[str]
        headers: Optional[Any]
        http_method: str
        query_parameters: Optional[Any]
        query_parameters_template: Optional[str]
        query_time_format: str
        query_window_in_min: int
        rate_limit_qps: Optional[int]
        retry_count: Optional[int]
        start_time_attribute_name: Optional[str]
        timeout_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                api_endpoint: str, 
                end_time_attribute_name: Optional[str] = ..., 
                headers: Optional[Any] = ..., 
                http_method: str, 
                query_parameters: Optional[Any] = ..., 
                query_parameters_template: Optional[str] = ..., 
                query_time_format: str, 
                query_window_in_min: int, 
                rate_limit_qps: Optional[int] = ..., 
                retry_count: Optional[int] = ..., 
                start_time_attribute_name: Optional[str] = ..., 
                timeout_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessConnectorPollingResponseProperties(_Model):
        events_json_paths: list[str]
        is_gzip_compressed: Optional[bool]
        success_status_json_path: Optional[str]
        success_status_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                events_json_paths: list[str], 
                is_gzip_compressed: Optional[bool] = ..., 
                success_status_json_path: Optional[str] = ..., 
                success_status_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessParameters(_Model):
        connector_ui_config: Optional[CodelessUiConnectorConfigProperties]

        @overload
        def __init__(
                self, 
                *, 
                connector_ui_config: Optional[CodelessUiConnectorConfigProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigProperties(_Model):
        availability: Availability
        connectivity_criteria: list[CodelessUiConnectorConfigPropertiesConnectivityCriteriaItem]
        custom_image: Optional[str]
        data_types: list[CodelessUiConnectorConfigPropertiesDataTypesItem]
        description_markdown: str
        graph_queries: list[CodelessUiConnectorConfigPropertiesGraphQueriesItem]
        graph_queries_table_name: str
        instruction_steps: list[CodelessUiConnectorConfigPropertiesInstructionStepsItem]
        permissions: Permissions
        publisher: str
        sample_queries: list[CodelessUiConnectorConfigPropertiesSampleQueriesItem]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                availability: Availability, 
                connectivity_criteria: list[CodelessUiConnectorConfigPropertiesConnectivityCriteriaItem], 
                custom_image: Optional[str] = ..., 
                data_types: list[CodelessUiConnectorConfigPropertiesDataTypesItem], 
                description_markdown: str, 
                graph_queries: list[CodelessUiConnectorConfigPropertiesGraphQueriesItem], 
                graph_queries_table_name: str, 
                instruction_steps: list[CodelessUiConnectorConfigPropertiesInstructionStepsItem], 
                permissions: Permissions, 
                publisher: str, 
                sample_queries: list[CodelessUiConnectorConfigPropertiesSampleQueriesItem], 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigPropertiesConnectivityCriteriaItem(ConnectivityCriteria):
        type: Union[str, ConnectivityType]
        value: list[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ConnectivityType]] = ..., 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigPropertiesDataTypesItem(LastDataReceivedDataType):
        last_data_received_query: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                last_data_received_query: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigPropertiesGraphQueriesItem(GraphQueries):
        base_query: str
        legend: str
        metric_name: str

        @overload
        def __init__(
                self, 
                *, 
                base_query: Optional[str] = ..., 
                legend: Optional[str] = ..., 
                metric_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigPropertiesInstructionStepsItem(InstructionSteps):
        description: str
        instructions: list[InstructionStepsInstructionsItem]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                instructions: Optional[list[InstructionStepsInstructionsItem]] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessUiConnectorConfigPropertiesSampleQueriesItem(SampleQueries):
        description: str
        query: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CodelessUiDataConnector(DataConnector, discriminator='GenericUI'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.GENERIC_UI]
        name: str
        properties: Optional[CodelessParameters]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[CodelessParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ConditionClause(_Model):
        clause_connective: Optional[Union[str, Connective]]
        field: str
        operator: Union[str, Operator]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                field: str, 
                operator: Union[str, Operator], 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ConditionProperties(_Model):
        clauses: list[ConditionClause]
        condition_connective: Optional[Union[str, Connective]]
        stix_object_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                clauses: list[ConditionClause]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.securityinsight.models.ConnectedEntity(_Model):
        additional_data: Optional[Any]
        target_entity_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_data: Optional[Any] = ..., 
                target_entity_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Connective(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AND = "And"
        OR = "Or"


    class azure.mgmt.securityinsight.models.ConnectivityCriteria(_Model):
        type: Optional[Union[str, ConnectivityType]]
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ConnectivityType]] = ..., 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ConnectivityCriterion(_Model):
        type: str
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                type: str, 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ConnectivityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IS_CONNECTED_QUERY = "IsConnectedQuery"


    class azure.mgmt.securityinsight.models.ConnectorDataType(_Model):
        last_data_received_query: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                last_data_received_query: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ConnectorDefinitionsAvailability(_Model):
        is_preview: Optional[bool]
        status: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                is_preview: Optional[bool] = ..., 
                status: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ConnectorDefinitionsPermissions(_Model):
        customs: Optional[list[CustomPermissionDetails]]
        licenses: Optional[list[str]]
        resource_provider: Optional[list[ConnectorDefinitionsResourceProvider]]
        tenant: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                customs: Optional[list[CustomPermissionDetails]] = ..., 
                licenses: Optional[list[str]] = ..., 
                resource_provider: Optional[list[ConnectorDefinitionsResourceProvider]] = ..., 
                tenant: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ConnectorDefinitionsResourceProvider(_Model):
        permissions_display_text: str
        provider: str
        provider_display_name: str
        required_permissions: ResourceProviderRequiredPermissions
        scope: Union[str, ProviderPermissionsScope]

        @overload
        def __init__(
                self, 
                *, 
                permissions_display_text: str, 
                provider: str, 
                provider_display_name: str, 
                required_permissions: ResourceProviderRequiredPermissions, 
                scope: Union[str, ProviderPermissionsScope]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ConnectorInstructionModelBase(_Model):
        parameters: Optional[Any]
        type: Union[str, SettingType]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[Any] = ..., 
                type: Union[str, SettingType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYTICS_RULE = "AnalyticsRule"
        AUTOMATION_RULE = "AutomationRule"
        HUNTING_QUERY = "HuntingQuery"
        PARSER = "Parser"
        PLAYBOOK = "Playbook"
        WORKBOOK = "Workbook"


    class azure.mgmt.securityinsight.models.CountQuery(_Model):
        properties: Optional[QueryProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QueryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.securityinsight.models.CustomEntityQuery(ResourceWithEtag):
        etag: str
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CustomEntityQueryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"


    class azure.mgmt.securityinsight.models.CustomPermissionDetails(_Model):
        description: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CustomizableConnectionsConfig(_Model):
        template_spec_name: str
        template_spec_version: str

        @overload
        def __init__(
                self, 
                *, 
                template_spec_name: str, 
                template_spec_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CustomizableConnectorDefinition(DataConnectorDefinition, discriminator='Customizable'):
        etag: str
        id: str
        kind: Literal[DataConnectorDefinitionKind.CUSTOMIZABLE]
        name: str
        properties: Optional[CustomizableConnectorDefinitionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[CustomizableConnectorDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.CustomizableConnectorDefinitionProperties(_Model):
        connections_config: Optional[CustomizableConnectionsConfig]
        connector_ui_config: CustomizableConnectorUiConfig
        created_time_utc: Optional[datetime]
        last_modified_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                connections_config: Optional[CustomizableConnectionsConfig] = ..., 
                connector_ui_config: CustomizableConnectorUiConfig, 
                created_time_utc: Optional[datetime] = ..., 
                last_modified_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CustomizableConnectorUiConfig(_Model):
        availability: Optional[ConnectorDefinitionsAvailability]
        connectivity_criteria: list[ConnectivityCriterion]
        data_types: list[ConnectorDataType]
        description_markdown: str
        graph_queries: list[GraphQuery]
        id: Optional[str]
        instruction_steps: list[InstructionStep]
        is_connectivity_criterias_match_some: Optional[bool]
        logo: Optional[str]
        permissions: ConnectorDefinitionsPermissions
        publisher: str
        title: str

        @overload
        def __init__(
                self, 
                *, 
                availability: Optional[ConnectorDefinitionsAvailability] = ..., 
                connectivity_criteria: list[ConnectivityCriterion], 
                data_types: list[ConnectorDataType], 
                description_markdown: str, 
                graph_queries: list[GraphQuery], 
                id: Optional[str] = ..., 
                instruction_steps: list[InstructionStep], 
                is_connectivity_criterias_match_some: Optional[bool] = ..., 
                logo: Optional[str] = ..., 
                permissions: ConnectorDefinitionsPermissions, 
                publisher: str, 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Customs(CustomsPermission):
        description: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.CustomsPermission(_Model):
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


    class azure.mgmt.securityinsight.models.DCRConfiguration(_Model):
        data_collection_endpoint: str
        data_collection_rule_immutable_id: str
        stream_name: str

        @overload
        def __init__(
                self, 
                *, 
                data_collection_endpoint: str, 
                data_collection_rule_immutable_id: str, 
                stream_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.DataConnector(ProxyResource):
        etag: Optional[str]
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.DataConnectorAuthorizationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.securityinsight.models.DataConnectorConnectBody(_Model):
        api_key: Optional[str]
        authorization_code: Optional[str]
        client_id: Optional[str]
        client_secret: Optional[str]
        data_collection_endpoint: Optional[str]
        data_collection_rule_immutable_id: Optional[str]
        kind: Optional[Union[str, ConnectAuthKind]]
        output_stream: Optional[str]
        password: Optional[str]
        request_config_user_input_values: Optional[list[Any]]
        user_name: Optional[str]

        @overload
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
                request_config_user_input_values: Optional[list[Any]] = ..., 
                user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.DataConnectorDataTypeCommon(_Model):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.DataConnectorDefinition(ProxyResource):
        etag: Optional[str]
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.DataConnectorDefinitionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMIZABLE = "Customizable"


    class azure.mgmt.securityinsight.models.DataConnectorKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMAZON_WEB_SERVICES_CLOUD_TRAIL = "AmazonWebServicesCloudTrail"
        AMAZON_WEB_SERVICES_S3 = "AmazonWebServicesS3"
        API_POLLING = "APIPolling"
        AZURE_ACTIVE_DIRECTORY = "AzureActiveDirectory"
        AZURE_ADVANCED_THREAT_PROTECTION = "AzureAdvancedThreatProtection"
        AZURE_SECURITY_CENTER = "AzureSecurityCenter"
        DYNAMICS365 = "Dynamics365"
        GCP = "GCP"
        GENERIC_UI = "GenericUI"
        IOT = "IOT"
        MICROSOFT_CLOUD_APP_SECURITY = "MicrosoftCloudAppSecurity"
        MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION = "MicrosoftDefenderAdvancedThreatProtection"
        MICROSOFT_PURVIEW_INFORMATION_PROTECTION = "MicrosoftPurviewInformationProtection"
        MICROSOFT_THREAT_INTELLIGENCE = "MicrosoftThreatIntelligence"
        MICROSOFT_THREAT_PROTECTION = "MicrosoftThreatProtection"
        OFFICE365 = "Office365"
        OFFICE365_PROJECT = "Office365Project"
        OFFICE_ATP = "OfficeATP"
        OFFICE_IRM = "OfficeIRM"
        OFFICE_POWER_BI = "OfficePowerBI"
        PREMIUM_MICROSOFT_DEFENDER_FOR_THREAT_INTELLIGENCE = "PremiumMicrosoftDefenderForThreatIntelligence"
        PURVIEW_AUDIT = "PurviewAudit"
        REST_API_POLLER = "RestApiPoller"
        THREAT_INTELLIGENCE = "ThreatIntelligence"
        THREAT_INTELLIGENCE_TAXII = "ThreatIntelligenceTaxii"


    class azure.mgmt.securityinsight.models.DataConnectorLicenseState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        UNKNOWN = "Unknown"
        VALID = "Valid"


    class azure.mgmt.securityinsight.models.DataConnectorRequirementsState(_Model):
        authorization_state: Optional[Union[str, DataConnectorAuthorizationState]]
        license_state: Optional[Union[str, DataConnectorLicenseState]]

        @overload
        def __init__(
                self, 
                *, 
                authorization_state: Optional[Union[str, DataConnectorAuthorizationState]] = ..., 
                license_state: Optional[Union[str, DataConnectorLicenseState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.DataConnectorTenantId(_Model):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.DataConnectorWithAlertsProperties(_Model):
        data_types: Optional[AlertsDataTypeOfDataConnector]

        @overload
        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.DataConnectorsCheckRequirements(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.DataTypeDefinitions(_Model):
        data_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.securityinsight.models.Deployment(_Model):
        deployment_id: Optional[str]
        deployment_logs_url: Optional[str]
        deployment_result: Optional[Union[str, DeploymentResult]]
        deployment_state: Optional[Union[str, DeploymentState]]
        deployment_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                deployment_id: Optional[str] = ..., 
                deployment_logs_url: Optional[str] = ..., 
                deployment_result: Optional[Union[str, DeploymentResult]] = ..., 
                deployment_state: Optional[Union[str, DeploymentState]] = ..., 
                deployment_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.DeploymentFetchStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_FOUND = "NotFound"
        SUCCESS = "Success"
        UNAUTHORIZED = "Unauthorized"


    class azure.mgmt.securityinsight.models.DeploymentInfo(_Model):
        deployment: Optional[Deployment]
        deployment_fetch_status: Optional[Union[str, DeploymentFetchStatus]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                deployment: Optional[Deployment] = ..., 
                deployment_fetch_status: Optional[Union[str, DeploymentFetchStatus]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.securityinsight.models.DnsEntity(Entity, discriminator='DnsResolution'):
        id: str
        kind: Literal[EntityKind.DNS_RESOLUTION]
        name: str
        properties: Optional[DnsEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DnsEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.DnsEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        dns_server_ip_entity_id: Optional[str]
        domain_name: Optional[str]
        friendly_name: str
        host_ip_address_entity_id: Optional[str]
        ip_address_entity_ids: Optional[list[str]]


    class azure.mgmt.securityinsight.models.Dynamics365CheckRequirements(DataConnectorsCheckRequirements, discriminator='Dynamics365'):
        kind: Literal[DataConnectorKind.DYNAMICS365]
        properties: Optional[Dynamics365CheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[Dynamics365CheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.Dynamics365CheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Dynamics365DataConnector(DataConnector, discriminator='Dynamics365'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.DYNAMICS365]
        name: str
        properties: Optional[Dynamics365DataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[Dynamics365DataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.Dynamics365DataConnectorDataTypes(_Model):
        dynamics365_cds_activities: Dynamics365DataConnectorDataTypesDynamics365CdsActivities

        @overload
        def __init__(
                self, 
                *, 
                dynamics365_cds_activities: Dynamics365DataConnectorDataTypesDynamics365CdsActivities
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Dynamics365DataConnectorDataTypesDynamics365CdsActivities(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Dynamics365DataConnectorProperties(DataConnectorTenantId):
        data_types: Dynamics365DataConnectorDataTypes
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: Dynamics365DataConnectorDataTypes, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ElevationToken(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        FULL = "Full"
        LIMITED = "Limited"


    class azure.mgmt.securityinsight.models.EnrichmentDomainBody(_Model):
        domain: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                domain: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EnrichmentDomainWhois(_Model):
        created: Optional[datetime]
        domain: Optional[str]
        expires: Optional[datetime]
        parsed_whois: Optional[EnrichmentDomainWhoisDetails]
        server: Optional[str]
        updated: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                domain: Optional[str] = ..., 
                expires: Optional[datetime] = ..., 
                parsed_whois: Optional[EnrichmentDomainWhoisDetails] = ..., 
                server: Optional[str] = ..., 
                updated: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EnrichmentDomainWhoisContact(_Model):
        city: Optional[str]
        country: Optional[str]
        email: Optional[str]
        fax: Optional[str]
        name: Optional[str]
        org: Optional[str]
        phone: Optional[str]
        postal: Optional[str]
        state: Optional[str]
        street: Optional[list[str]]

        @overload
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
                street: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EnrichmentDomainWhoisContacts(_Model):
        admin: Optional[EnrichmentDomainWhoisContact]
        billing: Optional[EnrichmentDomainWhoisContact]
        registrant: Optional[EnrichmentDomainWhoisContact]
        tech: Optional[EnrichmentDomainWhoisContact]

        @overload
        def __init__(
                self, 
                *, 
                admin: Optional[EnrichmentDomainWhoisContact] = ..., 
                billing: Optional[EnrichmentDomainWhoisContact] = ..., 
                registrant: Optional[EnrichmentDomainWhoisContact] = ..., 
                tech: Optional[EnrichmentDomainWhoisContact] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EnrichmentDomainWhoisDetails(_Model):
        contacts: Optional[EnrichmentDomainWhoisContacts]
        name_servers: Optional[list[str]]
        registrar: Optional[EnrichmentDomainWhoisRegistrarDetails]
        statuses: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                contacts: Optional[EnrichmentDomainWhoisContacts] = ..., 
                name_servers: Optional[list[str]] = ..., 
                registrar: Optional[EnrichmentDomainWhoisRegistrarDetails] = ..., 
                statuses: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EnrichmentDomainWhoisRegistrarDetails(_Model):
        abuse_contact_email: Optional[str]
        abuse_contact_phone: Optional[str]
        iana_id: Optional[str]
        name: Optional[str]
        url: Optional[str]
        whois_server: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                abuse_contact_email: Optional[str] = ..., 
                abuse_contact_phone: Optional[str] = ..., 
                iana_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                url: Optional[str] = ..., 
                whois_server: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EnrichmentIpAddressBody(_Model):
        ip_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EnrichmentIpGeodata(_Model):
        asn: Optional[str]
        carrier: Optional[str]
        city: Optional[str]
        city_confidence_factor: Optional[int]
        continent: Optional[str]
        country: Optional[str]
        country_confidence_factor: Optional[int]
        ip_addr: Optional[str]
        ip_routing_type: Optional[str]
        latitude: Optional[str]
        longitude: Optional[str]
        organization: Optional[str]
        organization_type: Optional[str]
        region: Optional[str]
        state: Optional[str]
        state_code: Optional[str]
        state_confidence_factor: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                asn: Optional[str] = ..., 
                carrier: Optional[str] = ..., 
                city: Optional[str] = ..., 
                city_confidence_factor: Optional[int] = ..., 
                continent: Optional[str] = ..., 
                country: Optional[str] = ..., 
                country_confidence_factor: Optional[int] = ..., 
                ip_addr: Optional[str] = ..., 
                ip_routing_type: Optional[str] = ..., 
                latitude: Optional[str] = ..., 
                longitude: Optional[str] = ..., 
                organization: Optional[str] = ..., 
                organization_type: Optional[str] = ..., 
                region: Optional[str] = ..., 
                state: Optional[str] = ..., 
                state_code: Optional[str] = ..., 
                state_confidence_factor: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EnrichmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAIN = "main"


    class azure.mgmt.securityinsight.models.Entity(ProxyResource):
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityAnalytics(Settings, discriminator='EntityAnalytics'):
        etag: str
        id: str
        kind: Literal[SettingKind.ENTITY_ANALYTICS]
        name: str
        properties: Optional[EntityAnalyticsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[EntityAnalyticsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.EntityAnalyticsProperties(_Model):
        entity_providers: Optional[list[Union[str, EntityProviders]]]

        @overload
        def __init__(
                self, 
                *, 
                entity_providers: Optional[list[Union[str, EntityProviders]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityCommonProperties(_Model):
        additional_data: Optional[dict[str, Any]]
        friendly_name: Optional[str]


    class azure.mgmt.securityinsight.models.EntityEdges(_Model):
        additional_data: Optional[dict[str, Any]]
        target_entity_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_data: Optional[dict[str, Any]] = ..., 
                target_entity_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityExpandParameters(_Model):
        end_time: Optional[datetime]
        expansion_id: Optional[str]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                expansion_id: Optional[str] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityExpandResponse(_Model):
        meta_data: Optional[ExpansionResultsMetadata]
        value: Optional[EntityExpandResponseValue]

        @overload
        def __init__(
                self, 
                *, 
                meta_data: Optional[ExpansionResultsMetadata] = ..., 
                value: Optional[EntityExpandResponseValue] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityExpandResponseValue(_Model):
        edges: Optional[list[EntityEdges]]
        entities: Optional[list[Entity]]

        @overload
        def __init__(
                self, 
                *, 
                edges: Optional[list[EntityEdges]] = ..., 
                entities: Optional[list[Entity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityFieldMapping(_Model):
        identifier: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityGetInsightsParameters(_Model):
        add_default_extended_time_range: Optional[bool]
        end_time: datetime
        insight_query_ids: Optional[list[str]]
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                add_default_extended_time_range: Optional[bool] = ..., 
                end_time: datetime, 
                insight_query_ids: Optional[list[str]] = ..., 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityGetInsightsResponse(_Model):
        meta_data: Optional[GetInsightsResultsMetadata]
        value: Optional[list[EntityInsightItem]]

        @overload
        def __init__(
                self, 
                *, 
                meta_data: Optional[GetInsightsResultsMetadata] = ..., 
                value: Optional[list[EntityInsightItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityInsightItem(_Model):
        chart_query_results: Optional[list[InsightsTableResult]]
        query_id: Optional[str]
        query_time_interval: Optional[EntityInsightItemQueryTimeInterval]
        table_query_results: Optional[InsightsTableResult]

        @overload
        def __init__(
                self, 
                *, 
                chart_query_results: Optional[list[InsightsTableResult]] = ..., 
                query_id: Optional[str] = ..., 
                query_time_interval: Optional[EntityInsightItemQueryTimeInterval] = ..., 
                table_query_results: Optional[InsightsTableResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityInsightItemQueryTimeInterval(_Model):
        end_time: Optional[datetime]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.securityinsight.models.EntityManualTriggerRequestBody(_Model):
        incident_arm_id: Optional[str]
        logic_apps_resource_id: str
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                incident_arm_id: Optional[str] = ..., 
                logic_apps_resource_id: str, 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityMapping(_Model):
        entity_type: Optional[Union[str, EntityMappingType]]
        field_mappings: Optional[list[FieldMapping]]

        @overload
        def __init__(
                self, 
                *, 
                entity_type: Optional[Union[str, EntityMappingType]] = ..., 
                field_mappings: Optional[list[FieldMapping]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.securityinsight.models.EntityQuery(ProxyResource):
        etag: Optional[str]
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityQueryItem(_Model):
        id: Optional[str]
        kind: str
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityQueryItemProperties(_Model):
        data_types: Optional[list[EntityQueryItemPropertiesDataTypesItem]]
        entities_filter: Optional[Any]
        input_entity_type: Optional[Union[str, EntityType]]
        required_input_fields_sets: Optional[list[list[str]]]

        @overload
        def __init__(
                self, 
                *, 
                data_types: Optional[list[EntityQueryItemPropertiesDataTypesItem]] = ..., 
                entities_filter: Optional[Any] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                required_input_fields_sets: Optional[list[list[str]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityQueryItemPropertiesDataTypesItem(_Model):
        data_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityQueryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"
        EXPANSION = "Expansion"
        INSIGHT = "Insight"


    class azure.mgmt.securityinsight.models.EntityQueryTemplate(ProxyResource):
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityQueryTemplateKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"
        ANOMALY = "Anomaly"
        BOOKMARK = "Bookmark"
        EXPANSION = "Expansion"
        GUIDED_INSIGHT = "GuidedInsight"
        INSIGHT = "Insight"
        SECURITY_ALERT = "SecurityAlert"


    class azure.mgmt.securityinsight.models.EntityTimelineItem(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityTimelineKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"
        ANOMALY = "Anomaly"
        BOOKMARK = "Bookmark"
        SECURITY_ALERT = "SecurityAlert"


    class azure.mgmt.securityinsight.models.EntityTimelineParameters(_Model):
        end_time: datetime
        kinds: Optional[list[Union[str, EntityTimelineKind]]]
        number_of_bucket: Optional[int]
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                end_time: datetime, 
                kinds: Optional[list[Union[str, EntityTimelineKind]]] = ..., 
                number_of_bucket: Optional[int] = ..., 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EntityTimelineResponse(_Model):
        meta_data: Optional[TimelineResultsMetadata]
        value: Optional[list[EntityTimelineItem]]

        @overload
        def __init__(
                self, 
                *, 
                meta_data: Optional[TimelineResultsMetadata] = ..., 
                value: Optional[list[EntityTimelineItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.securityinsight.models.Error(_Model):
        error_message: str
        member_resource_name: str

        @overload
        def __init__(
                self, 
                *, 
                error_message: str, 
                member_resource_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.securityinsight.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.securityinsight.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EventGroupingAggregationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_PER_RESULT = "AlertPerResult"
        SINGLE_ALERT = "SingleAlert"


    class azure.mgmt.securityinsight.models.EventGroupingSettings(_Model):
        aggregation_kind: Optional[Union[str, EventGroupingAggregationKind]]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_kind: Optional[Union[str, EventGroupingAggregationKind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ExpansionEntityQueriesProperties(_Model):
        data_sources: Optional[list[str]]
        display_name: Optional[str]
        input_entity_type: Optional[Union[str, EntityType]]
        input_fields: Optional[list[str]]
        output_entity_types: Optional[list[Union[str, EntityType]]]
        query_template: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_sources: Optional[list[str]] = ..., 
                display_name: Optional[str] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                input_fields: Optional[list[str]] = ..., 
                output_entity_types: Optional[list[Union[str, EntityType]]] = ..., 
                query_template: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ExpansionEntityQuery(EntityQuery, discriminator='Expansion'):
        etag: str
        id: str
        kind: Literal[EntityQueryKind.EXPANSION]
        name: str
        properties: Optional[ExpansionEntityQueriesProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ExpansionEntityQueriesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ExpansionResultAggregation(_Model):
        aggregation_type: Optional[str]
        count: int
        display_name: Optional[str]
        entity_kind: Union[str, EntityKind]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                count: int, 
                display_name: Optional[str] = ..., 
                entity_kind: Union[str, EntityKind]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ExpansionResultsMetadata(_Model):
        aggregations: Optional[list[ExpansionResultAggregation]]

        @overload
        def __init__(
                self, 
                *, 
                aggregations: Optional[list[ExpansionResultAggregation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.EyesOn(Settings, discriminator='EyesOn'):
        etag: str
        id: str
        kind: Literal[SettingKind.EYES_ON]
        name: str
        properties: Optional[EyesOnSettingsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[EyesOnSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.EyesOnSettingsProperties(_Model):
        is_enabled: Optional[bool]


    class azure.mgmt.securityinsight.models.FieldMapping(_Model):
        column_name: Optional[str]
        identifier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                column_name: Optional[str] = ..., 
                identifier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FileEntity(Entity, discriminator='File'):
        id: str
        kind: Literal[EntityKind.FILE]
        name: str
        properties: Optional[FileEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FileEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.FileEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        directory: Optional[str]
        file_hash_entity_ids: Optional[list[str]]
        file_name: Optional[str]
        friendly_name: str
        host_entity_id: Optional[str]


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


    class azure.mgmt.securityinsight.models.FileHashEntity(Entity, discriminator='FileHash'):
        id: str
        kind: Literal[EntityKind.FILE_HASH]
        name: str
        properties: Optional[FileHashEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FileHashEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.FileHashEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        algorithm: Optional[Union[str, FileHashAlgorithm]]
        friendly_name: str
        hash_value: Optional[str]


    class azure.mgmt.securityinsight.models.FileImport(ProxyResource):
        id: str
        name: str
        properties: Optional[FileImportProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FileImportProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.FileImportContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC_INDICATOR = "BasicIndicator"
        STIX_INDICATOR = "StixIndicator"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.securityinsight.models.FileImportProperties(_Model):
        content_type: Union[str, FileImportContentType]
        created_time_utc: Optional[datetime]
        error_file: Optional[FileMetadata]
        errors_preview: Optional[list[ValidationError]]
        files_valid_until_time_utc: Optional[datetime]
        import_file: FileMetadata
        import_valid_until_time_utc: Optional[datetime]
        ingested_record_count: Optional[int]
        ingestion_mode: Union[str, IngestionMode]
        source: str
        state: Optional[Union[str, FileImportState]]
        total_record_count: Optional[int]
        valid_record_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                content_type: Union[str, FileImportContentType], 
                import_file: FileMetadata, 
                ingestion_mode: Union[str, IngestionMode], 
                source: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FileImportState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FATAL_ERROR = "FatalError"
        INGESTED = "Ingested"
        INGESTED_WITH_ERRORS = "IngestedWithErrors"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"
        UNSPECIFIED = "Unspecified"
        WAITING_FOR_UPLOAD = "WaitingForUpload"


    class azure.mgmt.securityinsight.models.FileMetadata(_Model):
        delete_status: Optional[Union[str, DeleteStatus]]
        file_content_uri: Optional[str]
        file_format: Optional[Union[str, FileFormat]]
        file_name: Optional[str]
        file_size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                file_format: Optional[Union[str, FileFormat]] = ..., 
                file_name: Optional[str] = ..., 
                file_size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Flag(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.securityinsight.models.FusionAlertRule(AlertRule, discriminator='Fusion'):
        etag: str
        id: str
        kind: Literal[AlertRuleKind.FUSION]
        name: str
        properties: Optional[FusionAlertRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[FusionAlertRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.FusionAlertRuleProperties(_Model):
        alert_rule_template_name: str
        description: Optional[str]
        display_name: Optional[str]
        enabled: bool
        last_modified_utc: Optional[datetime]
        scenario_exclusion_patterns: Optional[list[FusionScenarioExclusionPattern]]
        severity: Optional[Union[str, AlertSeverity]]
        source_settings: Optional[list[FusionSourceSettings]]
        sub_techniques: Optional[list[str]]
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                alert_rule_template_name: str, 
                enabled: bool, 
                scenario_exclusion_patterns: Optional[list[FusionScenarioExclusionPattern]] = ..., 
                source_settings: Optional[list[FusionSourceSettings]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FusionAlertRuleTemplate(AlertRuleTemplate, discriminator='Fusion'):
        id: str
        kind: Literal[AlertRuleKind.FUSION]
        name: str
        properties: Optional[FusionAlertRuleTemplateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FusionAlertRuleTemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.FusionAlertRuleTemplateProperties(_Model):
        alert_rules_created_by_template_count: Optional[int]
        created_date_utc: Optional[datetime]
        description: Optional[str]
        display_name: Optional[str]
        last_updated_date_utc: Optional[datetime]
        required_data_connectors: Optional[list[AlertRuleTemplateDataSource]]
        severity: Optional[Union[str, AlertSeverity]]
        source_settings: Optional[list[FusionTemplateSourceSetting]]
        status: Optional[Union[str, TemplateStatus]]
        sub_techniques: Optional[list[str]]
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[list[AlertRuleTemplateDataSource]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                source_settings: Optional[list[FusionTemplateSourceSetting]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                sub_techniques: Optional[list[str]] = ..., 
                tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FusionScenarioExclusionPattern(_Model):
        date_added_in_utc: str
        exclusion_pattern: str

        @overload
        def __init__(
                self, 
                *, 
                date_added_in_utc: str, 
                exclusion_pattern: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FusionSourceSettings(_Model):
        enabled: bool
        source_name: str
        source_sub_types: Optional[list[FusionSourceSubTypeSetting]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                source_name: str, 
                source_sub_types: Optional[list[FusionSourceSubTypeSetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FusionSourceSubTypeSetting(_Model):
        enabled: bool
        severity_filters: FusionSubTypeSeverityFilter
        source_sub_type_display_name: Optional[str]
        source_sub_type_name: str

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                severity_filters: FusionSubTypeSeverityFilter, 
                source_sub_type_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FusionSubTypeSeverityFilter(_Model):
        filters: Optional[list[FusionSubTypeSeverityFiltersItem]]
        is_supported: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                filters: Optional[list[FusionSubTypeSeverityFiltersItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FusionSubTypeSeverityFiltersItem(_Model):
        enabled: bool
        severity: Union[str, AlertSeverity]

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                severity: Union[str, AlertSeverity]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FusionTemplateSourceSetting(_Model):
        source_name: str
        source_sub_types: Optional[list[FusionTemplateSourceSubType]]

        @overload
        def __init__(
                self, 
                *, 
                source_name: str, 
                source_sub_types: Optional[list[FusionTemplateSourceSubType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FusionTemplateSourceSubType(_Model):
        severity_filter: FusionTemplateSubTypeSeverityFilter
        source_sub_type_display_name: Optional[str]
        source_sub_type_name: str

        @overload
        def __init__(
                self, 
                *, 
                severity_filter: FusionTemplateSubTypeSeverityFilter, 
                source_sub_type_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.FusionTemplateSubTypeSeverityFilter(_Model):
        is_supported: bool
        severity_filters: Optional[list[Union[str, AlertSeverity]]]

        @overload
        def __init__(
                self, 
                *, 
                is_supported: bool, 
                severity_filters: Optional[list[Union[str, AlertSeverity]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GCPAuthModel(CcpAuthConfig, discriminator='GCP'):
        project_number: str
        service_account_email: str
        type: Literal[CcpAuthType.GCP]
        workload_identity_provider_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_number: str, 
                service_account_email: str, 
                workload_identity_provider_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GCPAuthProperties(_Model):
        project_number: str
        service_account_email: str
        workload_identity_provider_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_number: str, 
                service_account_email: str, 
                workload_identity_provider_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GCPDataConnector(DataConnector, discriminator='GCP'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.GCP]
        name: str
        properties: Optional[GCPDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[GCPDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.GCPDataConnectorProperties(_Model):
        auth: GCPAuthProperties
        connector_definition_name: str
        dcr_config: Optional[DCRConfiguration]
        request: GCPRequestProperties

        @overload
        def __init__(
                self, 
                *, 
                auth: GCPAuthProperties, 
                connector_definition_name: str, 
                dcr_config: Optional[DCRConfiguration] = ..., 
                request: GCPRequestProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GCPRequestProperties(_Model):
        project_id: str
        subscription_names: list[str]

        @overload
        def __init__(
                self, 
                *, 
                project_id: str, 
                subscription_names: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GenericBlobSbsAuthModel(CcpAuthConfig, discriminator='ServiceBus'):
        credentials_config: Optional[dict[str, str]]
        storage_account_credentials_config: Optional[dict[str, str]]
        type: Literal[CcpAuthType.SERVICE_BUS]

        @overload
        def __init__(
                self, 
                *, 
                credentials_config: Optional[dict[str, str]] = ..., 
                storage_account_credentials_config: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GeoLocation(_Model):
        asn: Optional[int]
        city: Optional[str]
        country_code: Optional[str]
        country_name: Optional[str]
        latitude: Optional[float]
        longitude: Optional[float]
        state: Optional[str]


    class azure.mgmt.securityinsight.models.GetInsightsError(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSIGHT = "Insight"


    class azure.mgmt.securityinsight.models.GetInsightsErrorKind(_Model):
        error_message: str
        kind: Union[str, GetInsightsError]
        query_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_message: str, 
                kind: Union[str, GetInsightsError], 
                query_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GetInsightsResultsMetadata(_Model):
        errors: Optional[list[GetInsightsErrorKind]]
        total_count: int

        @overload
        def __init__(
                self, 
                *, 
                errors: Optional[list[GetInsightsErrorKind]] = ..., 
                total_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GitHubAuthModel(CcpAuthConfig, discriminator='GitHub'):
        installation_id: Optional[str]
        type: Literal[CcpAuthType.GIT_HUB]

        @overload
        def __init__(
                self, 
                *, 
                installation_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GitHubResourceInfo(_Model):
        app_installation_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_installation_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GraphQueries(_Model):
        base_query: Optional[str]
        legend: Optional[str]
        metric_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                base_query: Optional[str] = ..., 
                legend: Optional[str] = ..., 
                metric_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GraphQuery(_Model):
        base_query: str
        legend: str
        metric_name: str

        @overload
        def __init__(
                self, 
                *, 
                base_query: str, 
                legend: str, 
                metric_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.GroupingConfiguration(_Model):
        enabled: bool
        group_by_alert_details: Optional[list[Union[str, AlertDetail]]]
        group_by_custom_details: Optional[list[str]]
        group_by_entities: Optional[list[Union[str, EntityMappingType]]]
        lookback_duration: timedelta
        matching_method: Union[str, MatchingMethod]
        reopen_closed_incident: bool

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                group_by_alert_details: Optional[list[Union[str, AlertDetail]]] = ..., 
                group_by_custom_details: Optional[list[str]] = ..., 
                group_by_entities: Optional[list[Union[str, EntityMappingType]]] = ..., 
                lookback_duration: timedelta, 
                matching_method: Union[str, MatchingMethod], 
                reopen_closed_incident: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.HostEntity(Entity, discriminator='Host'):
        id: str
        kind: Literal[EntityKind.HOST]
        name: str
        properties: Optional[HostEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HostEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.HostEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        azure_id: Optional[str]
        dns_domain: Optional[str]
        friendly_name: str
        host_name: Optional[str]
        is_domain_joined: Optional[bool]
        net_bios_name: Optional[str]
        nt_domain: Optional[str]
        oms_agent_id: Optional[str]
        os_family: Optional[Union[str, OSFamily]]
        os_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                os_family: Optional[Union[str, OSFamily]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.HttpMethodVerb(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "DELETE"
        GET = "GET"
        POST = "POST"
        PUT = "PUT"


    class azure.mgmt.securityinsight.models.Hunt(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[HuntProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[HuntProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.HuntComment(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[HuntCommentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[HuntCommentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.HuntCommentProperties(_Model):
        message: str

        @overload
        def __init__(
                self, 
                *, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.HuntOwner(_Model):
        assigned_to: Optional[str]
        email: Optional[str]
        object_id: Optional[str]
        owner_type: Optional[Union[str, OwnerType]]
        user_principal_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assigned_to: Optional[str] = ..., 
                email: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                owner_type: Optional[Union[str, OwnerType]] = ..., 
                user_principal_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.HuntProperties(_Model):
        attack_tactics: Optional[list[Union[str, AttackTactic]]]
        attack_techniques: Optional[list[str]]
        description: str
        display_name: str
        hypothesis_status: Optional[Union[str, HypothesisStatus]]
        labels: Optional[list[str]]
        owner: Optional[HuntOwner]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                attack_tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                attack_techniques: Optional[list[str]] = ..., 
                description: str, 
                display_name: str, 
                hypothesis_status: Optional[Union[str, HypothesisStatus]] = ..., 
                labels: Optional[list[str]] = ..., 
                owner: Optional[HuntOwner] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.HuntRelation(ProxyResource):
        id: str
        name: str
        properties: Optional[HuntRelationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HuntRelationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.HuntRelationProperties(_Model):
        labels: Optional[list[str]]
        related_resource_id: str
        related_resource_kind: Optional[str]
        related_resource_name: Optional[str]
        relation_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                labels: Optional[list[str]] = ..., 
                related_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.HuntingBookmark(Entity, discriminator='Bookmark'):
        id: str
        kind: Literal[EntityKind.BOOKMARK]
        name: str
        properties: Optional[HuntingBookmarkProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HuntingBookmarkProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.HuntingBookmarkProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        created: Optional[datetime]
        created_by: Optional[UserInfo]
        display_name: str
        event_time: Optional[datetime]
        friendly_name: str
        incident_info: Optional[IncidentInfo]
        labels: Optional[list[str]]
        notes: Optional[str]
        query: str
        query_result: Optional[str]
        updated: Optional[datetime]
        updated_by: Optional[UserInfo]

        @overload
        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                created_by: Optional[UserInfo] = ..., 
                display_name: str, 
                event_time: Optional[datetime] = ..., 
                incident_info: Optional[IncidentInfo] = ..., 
                labels: Optional[list[str]] = ..., 
                notes: Optional[str] = ..., 
                query: str, 
                query_result: Optional[str] = ..., 
                updated: Optional[datetime] = ..., 
                updated_by: Optional[UserInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.HypothesisStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALIDATED = "Invalidated"
        UNKNOWN = "Unknown"
        VALIDATED = "Validated"


    class azure.mgmt.securityinsight.models.Identity(TIObject, discriminator='Identity'):
        id: str
        kind: Literal[TIObjectKind.IDENTITY]
        name: str
        properties: TIObjectCommonProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TIObjectCommonProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.Incident(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[IncidentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[IncidentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentAdditionalData(_Model):
        alert_product_names: Optional[list[str]]
        alerts_count: Optional[int]
        bookmarks_count: Optional[int]
        comments_count: Optional[int]
        merged_incident_number: Optional[str]
        merged_incident_url: Optional[str]
        provider_incident_url: Optional[str]
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]


    class azure.mgmt.securityinsight.models.IncidentAlertList(_Model):
        value: list[SecurityAlert]

        @overload
        def __init__(
                self, 
                *, 
                value: list[SecurityAlert]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentBookmarkList(_Model):
        value: list[HuntingBookmark]

        @overload
        def __init__(
                self, 
                *, 
                value: list[HuntingBookmark]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.securityinsight.models.IncidentComment(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[IncidentCommentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[IncidentCommentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentCommentProperties(_Model):
        author: Optional[ClientInfo]
        created_time_utc: Optional[datetime]
        last_modified_time_utc: Optional[datetime]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentConfiguration(_Model):
        create_incident: bool
        grouping_configuration: Optional[GroupingConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                create_incident: bool, 
                grouping_configuration: Optional[GroupingConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentEntitiesResponse(_Model):
        entities: Optional[list[Entity]]
        meta_data: Optional[list[IncidentEntitiesResultsMetadata]]

        @overload
        def __init__(
                self, 
                *, 
                entities: Optional[list[Entity]] = ..., 
                meta_data: Optional[list[IncidentEntitiesResultsMetadata]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentEntitiesResultsMetadata(_Model):
        count: int
        entity_kind: Union[str, EntityKind]

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                entity_kind: Union[str, EntityKind]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentInfo(_Model):
        incident_id: Optional[str]
        relation_name: Optional[str]
        severity: Optional[Union[str, IncidentSeverity]]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                incident_id: Optional[str] = ..., 
                relation_name: Optional[str] = ..., 
                severity: Optional[Union[str, IncidentSeverity]] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentLabel(_Model):
        label_name: str
        label_type: Optional[Union[str, IncidentLabelType]]

        @overload
        def __init__(
                self, 
                *, 
                label_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentLabelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_ASSIGNED = "AutoAssigned"
        USER = "User"


    class azure.mgmt.securityinsight.models.IncidentOwnerInfo(_Model):
        assigned_to: Optional[str]
        email: Optional[str]
        object_id: Optional[str]
        owner_type: Optional[Union[str, OwnerType]]
        user_principal_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assigned_to: Optional[str] = ..., 
                email: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                owner_type: Optional[Union[str, OwnerType]] = ..., 
                user_principal_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentProperties(_Model):
        additional_data: Optional[IncidentAdditionalData]
        classification: Optional[Union[str, IncidentClassification]]
        classification_comment: Optional[str]
        classification_reason: Optional[Union[str, IncidentClassificationReason]]
        created_time_utc: Optional[datetime]
        description: Optional[str]
        first_activity_time_utc: Optional[datetime]
        incident_number: Optional[int]
        incident_url: Optional[str]
        labels: Optional[list[IncidentLabel]]
        last_activity_time_utc: Optional[datetime]
        last_modified_time_utc: Optional[datetime]
        owner: Optional[IncidentOwnerInfo]
        provider_incident_id: Optional[str]
        provider_name: Optional[str]
        related_analytic_rule_ids: Optional[list[str]]
        severity: Union[str, IncidentSeverity]
        status: Union[str, IncidentStatus]
        team_information: Optional[TeamInformation]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                classification: Optional[Union[str, IncidentClassification]] = ..., 
                classification_comment: Optional[str] = ..., 
                classification_reason: Optional[Union[str, IncidentClassificationReason]] = ..., 
                description: Optional[str] = ..., 
                first_activity_time_utc: Optional[datetime] = ..., 
                labels: Optional[list[IncidentLabel]] = ..., 
                last_activity_time_utc: Optional[datetime] = ..., 
                owner: Optional[IncidentOwnerInfo] = ..., 
                severity: Union[str, IncidentSeverity], 
                status: Union[str, IncidentStatus], 
                team_information: Optional[TeamInformation] = ..., 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentPropertiesAction(_Model):
        classification: Optional[Union[str, IncidentClassification]]
        classification_comment: Optional[str]
        classification_reason: Optional[Union[str, IncidentClassificationReason]]
        labels: Optional[list[IncidentLabel]]
        owner: Optional[IncidentOwnerInfo]
        severity: Optional[Union[str, IncidentSeverity]]
        status: Optional[Union[str, IncidentStatus]]

        @overload
        def __init__(
                self, 
                *, 
                classification: Optional[Union[str, IncidentClassification]] = ..., 
                classification_comment: Optional[str] = ..., 
                classification_reason: Optional[Union[str, IncidentClassificationReason]] = ..., 
                labels: Optional[list[IncidentLabel]] = ..., 
                owner: Optional[IncidentOwnerInfo] = ..., 
                severity: Optional[Union[str, IncidentSeverity]] = ..., 
                status: Optional[Union[str, IncidentStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        INFORMATIONAL = "Informational"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.securityinsight.models.IncidentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CLOSED = "Closed"
        NEW = "New"


    class azure.mgmt.securityinsight.models.IncidentTask(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: IncidentTaskProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: IncidentTaskProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentTaskProperties(_Model):
        created_by: Optional[ClientInfo]
        created_time_utc: Optional[datetime]
        description: Optional[str]
        last_modified_by: Optional[ClientInfo]
        last_modified_time_utc: Optional[datetime]
        status: Union[str, IncidentTaskStatus]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                created_by: Optional[ClientInfo] = ..., 
                description: Optional[str] = ..., 
                last_modified_by: Optional[ClientInfo] = ..., 
                status: Union[str, IncidentTaskStatus], 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IncidentTaskStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        NEW = "New"


    class azure.mgmt.securityinsight.models.Indicator(TIObject, discriminator='Indicator'):
        id: str
        kind: Literal[TIObjectKind.INDICATOR]
        name: str
        observables: Optional[list[IndicatorObservablesItem]]
        properties: TIObjectCommonProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                observables: Optional[list[IndicatorObservablesItem]] = ..., 
                properties: Optional[TIObjectCommonProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.IndicatorObservablesItem(_Model):
        type: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IngestionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INGEST_ANY_VALID_RECORDS = "IngestAnyValidRecords"
        INGEST_ONLY_IF_ALL_ARE_VALID = "IngestOnlyIfAllAreValid"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.securityinsight.models.InsightQueryItem(EntityQueryItem, discriminator='Insight'):
        id: str
        kind: Literal[EntityQueryKind.INSIGHT]
        name: str
        properties: Optional[InsightQueryItemProperties]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[InsightQueryItemProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemProperties(EntityQueryItemProperties):
        additional_query: Optional[InsightQueryItemPropertiesAdditionalQuery]
        base_query: Optional[str]
        chart_query: Optional[Any]
        data_types: list[EntityQueryItemPropertiesDataTypesItem]
        default_time_range: Optional[InsightQueryItemPropertiesDefaultTimeRange]
        description: Optional[str]
        display_name: Optional[str]
        entities_filter: any
        input_entity_type: Union[str, EntityType]
        reference_time_range: Optional[InsightQueryItemPropertiesReferenceTimeRange]
        required_input_fields_sets: list[list[str]]
        table_query: Optional[InsightQueryItemPropertiesTableQuery]

        @overload
        def __init__(
                self, 
                *, 
                additional_query: Optional[InsightQueryItemPropertiesAdditionalQuery] = ..., 
                base_query: Optional[str] = ..., 
                chart_query: Optional[Any] = ..., 
                data_types: Optional[list[EntityQueryItemPropertiesDataTypesItem]] = ..., 
                default_time_range: Optional[InsightQueryItemPropertiesDefaultTimeRange] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                entities_filter: Optional[Any] = ..., 
                input_entity_type: Optional[Union[str, EntityType]] = ..., 
                reference_time_range: Optional[InsightQueryItemPropertiesReferenceTimeRange] = ..., 
                required_input_fields_sets: Optional[list[list[str]]] = ..., 
                table_query: Optional[InsightQueryItemPropertiesTableQuery] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesAdditionalQuery(_Model):
        query: Optional[str]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                query: Optional[str] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesDefaultTimeRange(_Model):
        after_range: Optional[str]
        before_range: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                after_range: Optional[str] = ..., 
                before_range: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesReferenceTimeRange(_Model):
        before_range: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                before_range: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesTableQuery(_Model):
        columns_definitions: Optional[list[InsightQueryItemPropertiesTableQueryColumnsDefinitionsItem]]
        queries_definitions: Optional[list[InsightQueryItemPropertiesTableQueryQueriesDefinitionsItem]]

        @overload
        def __init__(
                self, 
                *, 
                columns_definitions: Optional[list[InsightQueryItemPropertiesTableQueryColumnsDefinitionsItem]] = ..., 
                queries_definitions: Optional[list[InsightQueryItemPropertiesTableQueryQueriesDefinitionsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesTableQueryColumnsDefinitionsItem(_Model):
        header: Optional[str]
        output_type: Optional[Union[str, OutputType]]
        support_deep_link: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                header: Optional[str] = ..., 
                output_type: Optional[Union[str, OutputType]] = ..., 
                support_deep_link: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesTableQueryQueriesDefinitionsItem(_Model):
        filter: Optional[str]
        link_columns_definitions: Optional[list[InsightQueryItemPropertiesTableQueryQueriesDefinitionsPropertiesItemsItem]]
        project: Optional[str]
        summarize: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                link_columns_definitions: Optional[list[InsightQueryItemPropertiesTableQueryQueriesDefinitionsPropertiesItemsItem]] = ..., 
                project: Optional[str] = ..., 
                summarize: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InsightQueryItemPropertiesTableQueryQueriesDefinitionsPropertiesItemsItem(_Model):
        projected_name: Optional[str]
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                projected_name: Optional[str] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InsightsTableResult(_Model):
        columns: Optional[list[InsightsTableResultColumnsItem]]
        rows: Optional[list[list[str]]]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[InsightsTableResultColumnsItem]] = ..., 
                rows: Optional[list[list[str]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InsightsTableResultColumnsItem(_Model):
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


    class azure.mgmt.securityinsight.models.InstructionStep(_Model):
        description: Optional[str]
        inner_steps: Optional[list[InstructionStep]]
        instructions: Optional[list[InstructionStepDetails]]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                inner_steps: Optional[list[InstructionStep]] = ..., 
                instructions: Optional[list[InstructionStepDetails]] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InstructionStepDetails(_Model):
        parameters: Any
        type: str

        @overload
        def __init__(
                self, 
                *, 
                parameters: Any, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InstructionSteps(_Model):
        description: Optional[str]
        instructions: Optional[list[InstructionStepsInstructionsItem]]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                instructions: Optional[list[InstructionStepsInstructionsItem]] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.InstructionStepsInstructionsItem(ConnectorInstructionModelBase):
        parameters: any
        type: Union[str, SettingType]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[Any] = ..., 
                type: Union[str, SettingType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IoTCheckRequirements(DataConnectorsCheckRequirements, discriminator='IOT'):
        kind: Literal[DataConnectorKind.IOT]
        properties: Optional[IoTCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IoTCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.IoTCheckRequirementsProperties(_Model):
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IoTDataConnector(DataConnector, discriminator='IOT'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.IOT]
        name: str
        properties: Optional[IoTDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[IoTDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.IoTDataConnectorProperties(DataConnectorWithAlertsProperties):
        data_types: AlertsDataTypeOfDataConnector
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IoTDeviceEntity(Entity, discriminator='IoTDevice'):
        id: str
        kind: Literal[EntityKind.IO_T_DEVICE]
        name: str
        properties: Optional[IoTDeviceEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IoTDeviceEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.IoTDeviceEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        device_id: Optional[str]
        device_name: Optional[str]
        device_sub_type: Optional[str]
        device_type: Optional[str]
        edge_id: Optional[str]
        firmware_version: Optional[str]
        friendly_name: str
        host_entity_id: Optional[str]
        importance: Optional[Union[str, DeviceImportance]]
        iot_hub_entity_id: Optional[str]
        iot_security_agent_id: Optional[str]
        ip_address_entity_id: Optional[str]
        is_authorized: Optional[bool]
        is_programming: Optional[bool]
        is_scanner: Optional[bool]
        mac_address: Optional[str]
        model: Optional[str]
        nic_entity_ids: Optional[list[str]]
        operating_system: Optional[str]
        owners: Optional[list[str]]
        protocols: Optional[list[str]]
        purdue_layer: Optional[str]
        sensor: Optional[str]
        serial_number: Optional[str]
        site: Optional[str]
        source: Optional[str]
        threat_intelligence: Optional[list[ThreatIntelligence]]
        vendor: Optional[str]
        zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                importance: Optional[Union[str, DeviceImportance]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.IpEntity(Entity, discriminator='Ip'):
        id: str
        kind: Literal[EntityKind.IP]
        name: str
        properties: Optional[IpEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IpEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.IpEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        address: Optional[str]
        friendly_name: str
        location: Optional[GeoLocation]
        threat_intelligence: Optional[list[ThreatIntelligence]]


    class azure.mgmt.securityinsight.models.Job(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[JobProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[JobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.JobItem(_Model):
        errors: Optional[list[Error]]
        execution_time: Optional[datetime]
        resource_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                errors: Optional[list[Error]] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.JobProperties(_Model):
        end_time: Optional[datetime]
        error_message: Optional[str]
        items_property: Optional[list[JobItem]]
        provisioning_state: Optional[Union[str, JobProvisioningState]]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                items_property: Optional[list[JobItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.JobProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.securityinsight.models.JwtAuthModel(CcpAuthConfig, discriminator='JwtToken'):
        headers: Optional[dict[str, str]]
        is_credentials_in_headers: Optional[bool]
        is_json_request: Optional[bool]
        password: dict[str, str]
        query_parameters: Optional[dict[str, str]]
        request_timeout_in_seconds: Optional[int]
        token_endpoint: str
        type: Literal[CcpAuthType.JWT_TOKEN]
        user_name: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[dict[str, str]] = ..., 
                is_credentials_in_headers: Optional[bool] = ..., 
                is_json_request: Optional[bool] = ..., 
                password: dict[str, str], 
                query_parameters: Optional[dict[str, str]] = ..., 
                request_timeout_in_seconds: Optional[int] = ..., 
                token_endpoint: str, 
                user_name: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        CUSTOM_DETECTION = "CustomDetection"
        DATA_CONNECTOR = "DataConnector"
        DATA_TYPE = "DataType"
        HUNTING_QUERY = "HuntingQuery"
        INVESTIGATION_QUERY = "InvestigationQuery"
        LOGIC_APPS_CUSTOM_CONNECTOR = "LogicAppsCustomConnector"
        NOTEBOOK = "Notebook"
        PARSER = "Parser"
        PLAYBOOK = "Playbook"
        PLAYBOOK_TEMPLATE = "PlaybookTemplate"
        RESOURCES_DATA_CONNECTOR = "ResourcesDataConnector"
        SOLUTION = "Solution"
        STANDALONE = "Standalone"
        SUMMARY_RULE = "SummaryRule"
        WATCHLIST = "Watchlist"
        WATCHLIST_TEMPLATE = "WatchlistTemplate"
        WORKBOOK = "Workbook"
        WORKBOOK_TEMPLATE = "WorkbookTemplate"


    class azure.mgmt.securityinsight.models.LastDataReceivedDataType(_Model):
        last_data_received_query: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                last_data_received_query: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MCASCheckRequirements(DataConnectorsCheckRequirements, discriminator='MicrosoftCloudAppSecurity'):
        kind: Literal[DataConnectorKind.MICROSOFT_CLOUD_APP_SECURITY]
        properties: Optional[MCASCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MCASCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MCASCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MCASDataConnector(DataConnector, discriminator='MicrosoftCloudAppSecurity'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.MICROSOFT_CLOUD_APP_SECURITY]
        name: str
        properties: Optional[MCASDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[MCASDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MCASDataConnectorDataTypes(AlertsDataTypeOfDataConnector):
        alerts: DataConnectorDataTypeCommon
        discovery_logs: Optional[DataConnectorDataTypeCommon]

        @overload
        def __init__(
                self, 
                *, 
                alerts: DataConnectorDataTypeCommon, 
                discovery_logs: Optional[DataConnectorDataTypeCommon] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MCASDataConnectorProperties(DataConnectorTenantId):
        data_types: MCASDataConnectorDataTypes
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: MCASDataConnectorDataTypes, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MDATPCheckRequirements(DataConnectorsCheckRequirements, discriminator='MicrosoftDefenderAdvancedThreatProtection'):
        kind: Literal[DataConnectorKind.MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION]
        properties: Optional[MDATPCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MDATPCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MDATPCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MDATPDataConnector(DataConnector, discriminator='MicrosoftDefenderAdvancedThreatProtection'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION]
        name: str
        properties: Optional[MDATPDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[MDATPDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MDATPDataConnectorProperties(_Model):
        data_types: Optional[AlertsDataTypeOfDataConnector]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MLBehaviorAnalyticsAlertRule(AlertRule, discriminator='MLBehaviorAnalytics'):
        etag: str
        id: str
        kind: Literal[AlertRuleKind.ML_BEHAVIOR_ANALYTICS]
        name: str
        properties: Optional[MLBehaviorAnalyticsAlertRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[MLBehaviorAnalyticsAlertRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MLBehaviorAnalyticsAlertRuleProperties(_Model):
        alert_rule_template_name: str
        description: Optional[str]
        display_name: Optional[str]
        enabled: bool
        last_modified_utc: Optional[datetime]
        severity: Optional[Union[str, AlertSeverity]]
        sub_techniques: Optional[list[str]]
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                alert_rule_template_name: str, 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MLBehaviorAnalyticsAlertRuleTemplate(AlertRuleTemplate, discriminator='MLBehaviorAnalytics'):
        id: str
        kind: Literal[AlertRuleKind.ML_BEHAVIOR_ANALYTICS]
        name: str
        properties: Optional[MLBehaviorAnalyticsAlertRuleTemplateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MLBehaviorAnalyticsAlertRuleTemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


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

        @overload
        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[list[AlertRuleTemplateDataSource]] = ..., 
                severity: Union[str, AlertSeverity], 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MSTICheckRequirements(DataConnectorsCheckRequirements, discriminator='MicrosoftThreatIntelligence'):
        kind: Literal[DataConnectorKind.MICROSOFT_THREAT_INTELLIGENCE]
        properties: Optional[MSTICheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MSTICheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MSTICheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MSTIDataConnector(DataConnector, discriminator='MicrosoftThreatIntelligence'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.MICROSOFT_THREAT_INTELLIGENCE]
        name: str
        properties: Optional[MSTIDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[MSTIDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MSTIDataConnectorDataTypes(_Model):
        microsoft_emerging_threat_feed: MSTIDataConnectorDataTypesMicrosoftEmergingThreatFeed

        @overload
        def __init__(
                self, 
                *, 
                microsoft_emerging_threat_feed: MSTIDataConnectorDataTypesMicrosoftEmergingThreatFeed
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MSTIDataConnectorDataTypesMicrosoftEmergingThreatFeed(DataConnectorDataTypeCommon):
        lookback_period: datetime
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                lookback_period: datetime, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MSTIDataConnectorProperties(DataConnectorTenantId):
        data_types: MSTIDataConnectorDataTypes
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: MSTIDataConnectorDataTypes, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MTPCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MTPDataConnector(DataConnector, discriminator='MicrosoftThreatProtection'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.MICROSOFT_THREAT_PROTECTION]
        name: str
        properties: Optional[MTPDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[MTPDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MTPDataConnectorDataTypes(_Model):
        alerts: Optional[MTPDataConnectorDataTypesAlerts]
        incidents: MTPDataConnectorDataTypesIncidents

        @overload
        def __init__(
                self, 
                *, 
                alerts: Optional[MTPDataConnectorDataTypesAlerts] = ..., 
                incidents: MTPDataConnectorDataTypesIncidents
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MTPDataConnectorDataTypesAlerts(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MTPDataConnectorDataTypesIncidents(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MTPDataConnectorProperties(DataConnectorTenantId):
        data_types: MTPDataConnectorDataTypes
        filtered_providers: Optional[MtpFilteredProviders]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: MTPDataConnectorDataTypes, 
                filtered_providers: Optional[MtpFilteredProviders] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MailClusterEntity(Entity, discriminator='MailCluster'):
        id: str
        kind: Literal[EntityKind.MAIL_CLUSTER]
        name: str
        properties: Optional[MailClusterEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MailClusterEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MailClusterEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        cluster_group: Optional[str]
        cluster_query_end_time: Optional[datetime]
        cluster_query_start_time: Optional[datetime]
        cluster_source_identifier: Optional[str]
        cluster_source_type: Optional[str]
        count_by_delivery_status: Optional[Any]
        count_by_protection_status: Optional[Any]
        count_by_threat_type: Optional[Any]
        friendly_name: str
        is_volume_anomaly: Optional[bool]
        mail_count: Optional[int]
        network_message_ids: Optional[list[str]]
        query: Optional[str]
        query_time: Optional[datetime]
        source: Optional[str]
        threats: Optional[list[str]]


    class azure.mgmt.securityinsight.models.MailMessageEntity(Entity, discriminator='MailMessage'):
        id: str
        kind: Literal[EntityKind.MAIL_MESSAGE]
        name: str
        properties: Optional[MailMessageEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MailMessageEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MailMessageEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        antispam_direction: Optional[Union[str, AntispamMailDirection]]
        body_fingerprint_bin1: Optional[int]
        body_fingerprint_bin2: Optional[int]
        body_fingerprint_bin3: Optional[int]
        body_fingerprint_bin4: Optional[int]
        body_fingerprint_bin5: Optional[int]
        delivery_action: Optional[Union[str, DeliveryAction]]
        delivery_location: Optional[Union[str, DeliveryLocation]]
        file_entity_ids: Optional[list[str]]
        friendly_name: str
        internet_message_id: Optional[str]
        language: Optional[str]
        network_message_id: Optional[str]
        p1_sender: Optional[str]
        p1_sender_display_name: Optional[str]
        p1_sender_domain: Optional[str]
        p2_sender: Optional[str]
        p2_sender_display_name: Optional[str]
        p2_sender_domain: Optional[str]
        receive_date: Optional[datetime]
        recipient: Optional[str]
        sender_ip: Optional[str]
        subject: Optional[str]
        threat_detection_methods: Optional[list[str]]
        threats: Optional[list[str]]
        urls: Optional[list[str]]

        @overload
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
                delivery_location: Optional[Union[str, DeliveryLocation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MailboxEntity(Entity, discriminator='Mailbox'):
        id: str
        kind: Literal[EntityKind.MAILBOX]
        name: str
        properties: Optional[MailboxEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MailboxEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MailboxEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        display_name: Optional[str]
        external_directory_object_id: Optional[str]
        friendly_name: str
        mailbox_primary_address: Optional[str]
        upn: Optional[str]


    class azure.mgmt.securityinsight.models.MalwareEntity(Entity, discriminator='Malware'):
        id: str
        kind: Literal[EntityKind.MALWARE]
        name: str
        properties: Optional[MalwareEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MalwareEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MalwareEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        category: Optional[str]
        file_entity_ids: Optional[list[str]]
        friendly_name: str
        malware_name: Optional[str]
        process_entity_ids: Optional[list[str]]


    class azure.mgmt.securityinsight.models.ManualTriggerRequestBody(_Model):
        logic_apps_resource_id: str
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                logic_apps_resource_id: str, 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MatchingMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_ENTITIES = "AllEntities"
        ANY_ALERT = "AnyAlert"
        SELECTED = "Selected"


    class azure.mgmt.securityinsight.models.MetadataAuthor(_Model):
        email: Optional[str]
        link: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                link: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MetadataCategories(_Model):
        domains: Optional[list[str]]
        verticals: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                domains: Optional[list[str]] = ..., 
                verticals: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MetadataDependencies(_Model):
        content_id: Optional[str]
        criteria: Optional[list[MetadataDependencies]]
        kind: Optional[Union[str, Kind]]
        name: Optional[str]
        operator: Optional[Union[str, MetadataDependencyOperator]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_id: Optional[str] = ..., 
                criteria: Optional[list[MetadataDependencies]] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                name: Optional[str] = ..., 
                operator: Optional[Union[str, MetadataDependencyOperator]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MetadataDependencyOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AND = "AND"
        OR = "OR"


    class azure.mgmt.securityinsight.models.MetadataModel(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[MetadataProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[MetadataProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MetadataPatch(ResourceWithEtag):
        etag: str
        id: str
        name: str
        properties: Optional[MetadataPropertiesPatch]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[MetadataPropertiesPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MetadataProperties(_Model):
        author: Optional[MetadataAuthor]
        categories: Optional[MetadataCategories]
        content_id: Optional[str]
        content_schema_version: Optional[str]
        custom_version: Optional[str]
        dependencies: Optional[MetadataDependencies]
        first_publish_date: Optional[date]
        icon: Optional[str]
        kind: str
        last_publish_date: Optional[date]
        parent_id: str
        preview_images: Optional[list[str]]
        preview_images_dark: Optional[list[str]]
        providers: Optional[list[str]]
        source: Optional[MetadataSource]
        support: Optional[MetadataSupport]
        threat_analysis_tactics: Optional[list[str]]
        threat_analysis_techniques: Optional[list[str]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                author: Optional[MetadataAuthor] = ..., 
                categories: Optional[MetadataCategories] = ..., 
                content_id: Optional[str] = ..., 
                content_schema_version: Optional[str] = ..., 
                custom_version: Optional[str] = ..., 
                dependencies: Optional[MetadataDependencies] = ..., 
                first_publish_date: Optional[date] = ..., 
                icon: Optional[str] = ..., 
                kind: str, 
                last_publish_date: Optional[date] = ..., 
                parent_id: str, 
                preview_images: Optional[list[str]] = ..., 
                preview_images_dark: Optional[list[str]] = ..., 
                providers: Optional[list[str]] = ..., 
                source: Optional[MetadataSource] = ..., 
                support: Optional[MetadataSupport] = ..., 
                threat_analysis_tactics: Optional[list[str]] = ..., 
                threat_analysis_techniques: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MetadataPropertiesPatch(_Model):
        author: Optional[MetadataAuthor]
        categories: Optional[MetadataCategories]
        content_id: Optional[str]
        content_schema_version: Optional[str]
        custom_version: Optional[str]
        dependencies: Optional[MetadataDependencies]
        first_publish_date: Optional[date]
        icon: Optional[str]
        kind: Optional[str]
        last_publish_date: Optional[date]
        parent_id: Optional[str]
        preview_images: Optional[list[str]]
        preview_images_dark: Optional[list[str]]
        providers: Optional[list[str]]
        source: Optional[MetadataSource]
        support: Optional[MetadataSupport]
        threat_analysis_tactics: Optional[list[str]]
        threat_analysis_techniques: Optional[list[str]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                author: Optional[MetadataAuthor] = ..., 
                categories: Optional[MetadataCategories] = ..., 
                content_id: Optional[str] = ..., 
                content_schema_version: Optional[str] = ..., 
                custom_version: Optional[str] = ..., 
                dependencies: Optional[MetadataDependencies] = ..., 
                first_publish_date: Optional[date] = ..., 
                icon: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                last_publish_date: Optional[date] = ..., 
                parent_id: Optional[str] = ..., 
                preview_images: Optional[list[str]] = ..., 
                preview_images_dark: Optional[list[str]] = ..., 
                providers: Optional[list[str]] = ..., 
                source: Optional[MetadataSource] = ..., 
                support: Optional[MetadataSupport] = ..., 
                threat_analysis_tactics: Optional[list[str]] = ..., 
                threat_analysis_techniques: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MetadataSource(_Model):
        kind: Union[str, SourceKind]
        name: Optional[str]
        source_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: Union[str, SourceKind], 
                name: Optional[str] = ..., 
                source_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MetadataSupport(_Model):
        email: Optional[str]
        link: Optional[str]
        name: Optional[str]
        tier: Union[str, SupportTier]

        @overload
        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                link: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tier: Union[str, SupportTier]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftPurviewInformationProtectionCheckRequirements(DataConnectorsCheckRequirements, discriminator='MicrosoftPurviewInformationProtection'):
        kind: Literal[DataConnectorKind.MICROSOFT_PURVIEW_INFORMATION_PROTECTION]
        properties: Optional[MicrosoftPurviewInformationProtectionCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MicrosoftPurviewInformationProtectionCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftPurviewInformationProtectionCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftPurviewInformationProtectionConnectorDataTypes(_Model):
        logs: MicrosoftPurviewInformationProtectionConnectorDataTypesLogs

        @overload
        def __init__(
                self, 
                *, 
                logs: MicrosoftPurviewInformationProtectionConnectorDataTypesLogs
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftPurviewInformationProtectionConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftPurviewInformationProtectionDataConnector(DataConnector, discriminator='MicrosoftPurviewInformationProtection'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.MICROSOFT_PURVIEW_INFORMATION_PROTECTION]
        name: str
        properties: Optional[MicrosoftPurviewInformationProtectionDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[MicrosoftPurviewInformationProtectionDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftPurviewInformationProtectionDataConnectorProperties(DataConnectorTenantId):
        data_types: MicrosoftPurviewInformationProtectionConnectorDataTypes
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: MicrosoftPurviewInformationProtectionConnectorDataTypes, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityIncidentCreationAlertRule(AlertRule, discriminator='MicrosoftSecurityIncidentCreation'):
        etag: str
        id: str
        kind: Literal[AlertRuleKind.MICROSOFT_SECURITY_INCIDENT_CREATION]
        name: str
        properties: Optional[MicrosoftSecurityIncidentCreationAlertRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[MicrosoftSecurityIncidentCreationAlertRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityIncidentCreationAlertRuleCommonProperties(_Model):
        display_names_exclude_filter: Optional[list[str]]
        display_names_filter: Optional[list[str]]
        product_filter: Union[str, MicrosoftSecurityProductName]
        severities_filter: Optional[list[Union[str, AlertSeverity]]]

        @overload
        def __init__(
                self, 
                *, 
                display_names_exclude_filter: Optional[list[str]] = ..., 
                display_names_filter: Optional[list[str]] = ..., 
                product_filter: Union[str, MicrosoftSecurityProductName], 
                severities_filter: Optional[list[Union[str, AlertSeverity]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityIncidentCreationAlertRuleProperties(MicrosoftSecurityIncidentCreationAlertRuleCommonProperties):
        alert_rule_template_name: Optional[str]
        description: Optional[str]
        display_name: str
        display_names_exclude_filter: list[str]
        display_names_filter: list[str]
        enabled: bool
        last_modified_utc: Optional[datetime]
        product_filter: Union[str, MicrosoftSecurityProductName]
        severities_filter: Union[list[str, AlertSeverity]]

        @overload
        def __init__(
                self, 
                *, 
                alert_rule_template_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                display_names_exclude_filter: Optional[list[str]] = ..., 
                display_names_filter: Optional[list[str]] = ..., 
                enabled: bool, 
                product_filter: Union[str, MicrosoftSecurityProductName], 
                severities_filter: Optional[list[Union[str, AlertSeverity]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityIncidentCreationAlertRuleTemplate(AlertRuleTemplate, discriminator='MicrosoftSecurityIncidentCreation'):
        id: str
        kind: Literal[AlertRuleKind.MICROSOFT_SECURITY_INCIDENT_CREATION]
        name: str
        properties: Optional[MicrosoftSecurityIncidentCreationAlertRuleTemplateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MicrosoftSecurityIncidentCreationAlertRuleTemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityIncidentCreationAlertRuleTemplateProperties(AlertRuleTemplatePropertiesBase):
        alert_rules_created_by_template_count: int
        created_date_utc: datetime
        description: str
        display_name: str
        display_names_exclude_filter: Optional[list[str]]
        display_names_filter: Optional[list[str]]
        last_updated_date_utc: datetime
        product_filter: Optional[Union[str, MicrosoftSecurityProductName]]
        required_data_connectors: list[AlertRuleTemplateDataSource]
        severities_filter: Optional[list[Union[str, AlertSeverity]]]
        status: Union[str, TemplateStatus]

        @overload
        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                display_names_exclude_filter: Optional[list[str]] = ..., 
                display_names_filter: Optional[list[str]] = ..., 
                product_filter: Optional[Union[str, MicrosoftSecurityProductName]] = ..., 
                required_data_connectors: Optional[list[AlertRuleTemplateDataSource]] = ..., 
                severities_filter: Optional[list[Union[str, AlertSeverity]]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MicrosoftSecurityProductName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ACTIVE_DIRECTORY_IDENTITY_PROTECTION = "Azure Active Directory Identity Protection"
        AZURE_ADVANCED_THREAT_PROTECTION = "Azure Advanced Threat Protection"
        AZURE_SECURITY_CENTER = "Azure Security Center"
        AZURE_SECURITY_CENTER_FOR_IO_T = "Azure Security Center for IoT"
        MICROSOFT_CLOUD_APP_SECURITY = "Microsoft Cloud App Security"
        MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION = "Microsoft Defender Advanced Threat Protection"
        OFFICE365_ADVANCED_THREAT_PROTECTION = "Office 365 Advanced Threat Protection"


    class azure.mgmt.securityinsight.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.securityinsight.models.MtpCheckRequirements(DataConnectorsCheckRequirements, discriminator='MicrosoftThreatProtection'):
        kind: Literal[DataConnectorKind.MICROSOFT_THREAT_PROTECTION]
        properties: Optional[MTPCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MTPCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.MtpFilteredProviders(_Model):
        alerts: list[Union[str, MtpProvider]]

        @overload
        def __init__(
                self, 
                *, 
                alerts: list[Union[str, MtpProvider]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.MtpProvider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_DEFENDER_FOR_CLOUD_APPS = "microsoftDefenderForCloudApps"
        MICROSOFT_DEFENDER_FOR_IDENTITY = "microsoftDefenderForIdentity"


    class azure.mgmt.securityinsight.models.NicEntity(Entity, discriminator='Nic'):
        id: str
        kind: Literal[EntityKind.NIC]
        name: str
        properties: Optional[NicEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NicEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.NicEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        ip_address_entity_id: Optional[str]
        mac_address: Optional[str]
        vlans: Optional[list[str]]


    class azure.mgmt.securityinsight.models.NoneAuthModel(CcpAuthConfig, discriminator='None'):
        type: Literal[CcpAuthType.NONE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.NrtAlertRule(AlertRule, discriminator='NRT'):
        etag: str
        id: str
        kind: Literal[AlertRuleKind.NRT]
        name: str
        properties: Optional[NrtAlertRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[NrtAlertRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.NrtAlertRuleProperties(_Model):
        alert_details_override: Optional[AlertDetailsOverride]
        alert_rule_template_name: Optional[str]
        custom_details: Optional[dict[str, str]]
        description: Optional[str]
        display_name: str
        enabled: bool
        entity_mappings: Optional[list[EntityMapping]]
        event_grouping_settings: Optional[EventGroupingSettings]
        incident_configuration: Optional[IncidentConfiguration]
        last_modified_utc: Optional[datetime]
        query: str
        sentinel_entities_mappings: Optional[list[SentinelEntityMapping]]
        severity: Union[str, AlertSeverity]
        sub_techniques: Optional[list[str]]
        suppression_duration: timedelta
        suppression_enabled: bool
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]
        template_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                alert_rule_template_name: Optional[str] = ..., 
                custom_details: Optional[dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                enabled: bool, 
                entity_mappings: Optional[list[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                incident_configuration: Optional[IncidentConfiguration] = ..., 
                query: str, 
                sentinel_entities_mappings: Optional[list[SentinelEntityMapping]] = ..., 
                severity: Union[str, AlertSeverity], 
                sub_techniques: Optional[list[str]] = ..., 
                suppression_duration: timedelta, 
                suppression_enabled: bool, 
                tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[list[str]] = ..., 
                template_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.NrtAlertRuleTemplate(AlertRuleTemplate, discriminator='NRT'):
        id: str
        kind: Literal[AlertRuleKind.NRT]
        name: str
        properties: Optional[NrtAlertRuleTemplateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NrtAlertRuleTemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.NrtAlertRuleTemplateProperties(_Model):
        alert_details_override: Optional[AlertDetailsOverride]
        alert_rules_created_by_template_count: Optional[int]
        created_date_utc: Optional[datetime]
        custom_details: Optional[dict[str, str]]
        description: Optional[str]
        display_name: Optional[str]
        entity_mappings: Optional[list[EntityMapping]]
        event_grouping_settings: Optional[EventGroupingSettings]
        last_updated_date_utc: Optional[datetime]
        query: Optional[str]
        required_data_connectors: Optional[list[AlertRuleTemplateDataSource]]
        sentinel_entities_mappings: Optional[list[SentinelEntityMapping]]
        severity: Optional[Union[str, AlertSeverity]]
        status: Optional[Union[str, TemplateStatus]]
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                custom_details: Optional[dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                entity_mappings: Optional[list[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                query: Optional[str] = ..., 
                required_data_connectors: Optional[list[AlertRuleTemplateDataSource]] = ..., 
                sentinel_entities_mappings: Optional[list[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OAuthModel(CcpAuthConfig, discriminator='OAuth2'):
        access_token_prepend: Optional[str]
        authorization_code: Optional[str]
        authorization_endpoint: Optional[str]
        authorization_endpoint_headers: Optional[dict[str, str]]
        authorization_endpoint_query_parameters: Optional[dict[str, str]]
        client_id: str
        client_secret: str
        grant_type: str
        is_credentials_in_headers: Optional[bool]
        is_jwt_bearer_flow: Optional[bool]
        redirect_uri: Optional[str]
        scope: Optional[str]
        token_endpoint: str
        token_endpoint_headers: Optional[dict[str, str]]
        token_endpoint_query_parameters: Optional[dict[str, str]]
        type: Literal[CcpAuthType.O_AUTH2]

        @overload
        def __init__(
                self, 
                *, 
                access_token_prepend: Optional[str] = ..., 
                authorization_code: Optional[str] = ..., 
                authorization_endpoint: Optional[str] = ..., 
                authorization_endpoint_headers: Optional[dict[str, str]] = ..., 
                authorization_endpoint_query_parameters: Optional[dict[str, str]] = ..., 
                client_id: str, 
                client_secret: str, 
                grant_type: str, 
                is_credentials_in_headers: Optional[bool] = ..., 
                is_jwt_bearer_flow: Optional[bool] = ..., 
                redirect_uri: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                token_endpoint: str, 
                token_endpoint_headers: Optional[dict[str, str]] = ..., 
                token_endpoint_query_parameters: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OSFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANDROID = "Android"
        IOS = "IOS"
        LINUX = "Linux"
        UNKNOWN = "Unknown"
        WINDOWS = "Windows"


    class azure.mgmt.securityinsight.models.Office365ProjectCheckRequirements(DataConnectorsCheckRequirements, discriminator='Office365Project'):
        kind: Literal[DataConnectorKind.OFFICE365_PROJECT]
        properties: Optional[Office365ProjectCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[Office365ProjectCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.Office365ProjectCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Office365ProjectConnectorDataTypes(_Model):
        logs: Office365ProjectConnectorDataTypesLogs

        @overload
        def __init__(
                self, 
                *, 
                logs: Office365ProjectConnectorDataTypesLogs
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Office365ProjectConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Office365ProjectDataConnector(DataConnector, discriminator='Office365Project'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.OFFICE365_PROJECT]
        name: str
        properties: Optional[Office365ProjectDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[Office365ProjectDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.Office365ProjectDataConnectorProperties(DataConnectorTenantId):
        data_types: Office365ProjectConnectorDataTypes
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: Office365ProjectConnectorDataTypes, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeATPCheckRequirements(DataConnectorsCheckRequirements, discriminator='OfficeATP'):
        kind: Literal[DataConnectorKind.OFFICE_ATP]
        properties: Optional[OfficeATPCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OfficeATPCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeATPCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeATPDataConnector(DataConnector, discriminator='OfficeATP'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.OFFICE_ATP]
        name: str
        properties: Optional[OfficeATPDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[OfficeATPDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeATPDataConnectorProperties(_Model):
        data_types: Optional[AlertsDataTypeOfDataConnector]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeConsent(ProxyResource):
        id: str
        name: str
        properties: Optional[OfficeConsentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OfficeConsentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeConsentProperties(_Model):
        consent_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                consent_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnector(DataConnector, discriminator='Office365'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.OFFICE365]
        name: str
        properties: Optional[OfficeDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[OfficeDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnectorDataTypes(_Model):
        exchange: OfficeDataConnectorDataTypesExchange
        share_point: OfficeDataConnectorDataTypesSharePoint
        teams: OfficeDataConnectorDataTypesTeams

        @overload
        def __init__(
                self, 
                *, 
                exchange: OfficeDataConnectorDataTypesExchange, 
                share_point: OfficeDataConnectorDataTypesSharePoint, 
                teams: OfficeDataConnectorDataTypesTeams
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnectorDataTypesExchange(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnectorDataTypesSharePoint(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnectorDataTypesTeams(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeDataConnectorProperties(DataConnectorTenantId):
        data_types: OfficeDataConnectorDataTypes
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: OfficeDataConnectorDataTypes, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeIRMCheckRequirements(DataConnectorsCheckRequirements, discriminator='OfficeIRM'):
        kind: Literal[DataConnectorKind.OFFICE_IRM]
        properties: Optional[OfficeIRMCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OfficeIRMCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeIRMCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeIRMDataConnector(DataConnector, discriminator='OfficeIRM'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.OFFICE_IRM]
        name: str
        properties: Optional[OfficeIRMDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[OfficeIRMDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.OfficeIRMDataConnectorProperties(_Model):
        data_types: Optional[AlertsDataTypeOfDataConnector]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: Optional[AlertsDataTypeOfDataConnector] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficePowerBICheckRequirements(DataConnectorsCheckRequirements, discriminator='OfficePowerBI'):
        kind: Literal[DataConnectorKind.OFFICE_POWER_BI]
        properties: Optional[OfficePowerBICheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OfficePowerBICheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.OfficePowerBICheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficePowerBIConnectorDataTypes(_Model):
        logs: OfficePowerBIConnectorDataTypesLogs

        @overload
        def __init__(
                self, 
                *, 
                logs: OfficePowerBIConnectorDataTypesLogs
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficePowerBIConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OfficePowerBIDataConnector(DataConnector, discriminator='OfficePowerBI'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.OFFICE_POWER_BI]
        name: str
        properties: Optional[OfficePowerBIDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[OfficePowerBIDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.OfficePowerBIDataConnectorProperties(DataConnectorTenantId):
        data_types: OfficePowerBIConnectorDataTypes
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: OfficePowerBIConnectorDataTypes, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFTER_ABSOLUTE = "AfterAbsolute"
        AFTER_RELATIVE = "AfterRelative"
        ARRAY_CONTAINS = "ArrayContains"
        ARRAY_NOT_CONTAINS = "ArrayNotContains"
        BEFORE_ABSOLUTE = "BeforeAbsolute"
        BEFORE_RELATIVE = "BeforeRelative"
        EQUALS = "Equals"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_EQUAL = "GreaterThanEqual"
        IS_FALSE = "IsFalse"
        IS_NULL = "IsNull"
        IS_TRUE = "IsTrue"
        LESS_THAN = "LessThan"
        LESS_THAN_EQUAL = "LessThanEqual"
        NOT_EQUALS = "NotEquals"
        ON_OR_AFTER_ABSOLUTE = "OnOrAfterAbsolute"
        ON_OR_AFTER_RELATIVE = "OnOrAfterRelative"
        ON_OR_BEFORE_ABSOLUTE = "OnOrBeforeAbsolute"
        ON_OR_BEFORE_RELATIVE = "OnOrBeforeRelative"
        STRING_CONTAINS = "StringContains"
        STRING_ENDS_WITH = "StringEndsWith"
        STRING_IS_EMPTY = "StringIsEmpty"
        STRING_NOT_CONTAINS = "StringNotContains"
        STRING_NOT_ENDS_WITH = "StringNotEndsWith"
        STRING_NOT_STARTS_WITH = "StringNotStartsWith"
        STRING_STARTS_WITH = "StringStartsWith"


    class azure.mgmt.securityinsight.models.OracleAuthModel(CcpAuthConfig, discriminator='Oracle'):
        pem_file: str
        public_fingerprint: str
        tenant_id: str
        type: Literal[CcpAuthType.ORACLE]
        user_id: str

        @overload
        def __init__(
                self, 
                *, 
                pem_file: str, 
                public_fingerprint: str, 
                tenant_id: str, 
                user_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.OutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATE = "Date"
        ENTITY = "Entity"
        NUMBER = "Number"
        STRING = "String"


    class azure.mgmt.securityinsight.models.OwnerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "Group"
        UNKNOWN = "Unknown"
        USER = "User"


    class azure.mgmt.securityinsight.models.PackageBaseProperties(_Model):
        author: Optional[MetadataAuthor]
        categories: Optional[MetadataCategories]
        content_id: Optional[str]
        content_kind: Optional[Union[str, PackageKind]]
        content_product_id: Optional[str]
        content_schema_version: Optional[str]
        dependencies: Optional[MetadataDependencies]
        description: Optional[str]
        display_name: Optional[str]
        first_publish_date: Optional[date]
        icon: Optional[str]
        is_deprecated: Optional[Union[str, Flag]]
        is_featured: Optional[Union[str, Flag]]
        is_new: Optional[Union[str, Flag]]
        is_preview: Optional[Union[str, Flag]]
        last_publish_date: Optional[date]
        providers: Optional[list[str]]
        publisher_display_name: Optional[str]
        source: Optional[MetadataSource]
        support: Optional[MetadataSupport]
        threat_analysis_tactics: Optional[list[str]]
        threat_analysis_techniques: Optional[list[str]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                author: Optional[MetadataAuthor] = ..., 
                categories: Optional[MetadataCategories] = ..., 
                content_id: Optional[str] = ..., 
                content_kind: Optional[Union[str, PackageKind]] = ..., 
                content_product_id: Optional[str] = ..., 
                content_schema_version: Optional[str] = ..., 
                dependencies: Optional[MetadataDependencies] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                first_publish_date: Optional[date] = ..., 
                icon: Optional[str] = ..., 
                is_deprecated: Optional[Union[str, Flag]] = ..., 
                is_featured: Optional[Union[str, Flag]] = ..., 
                is_new: Optional[Union[str, Flag]] = ..., 
                is_preview: Optional[Union[str, Flag]] = ..., 
                last_publish_date: Optional[date] = ..., 
                providers: Optional[list[str]] = ..., 
                publisher_display_name: Optional[str] = ..., 
                source: Optional[MetadataSource] = ..., 
                support: Optional[MetadataSupport] = ..., 
                threat_analysis_tactics: Optional[list[str]] = ..., 
                threat_analysis_techniques: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PackageKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SOLUTION = "Solution"
        STANDALONE = "Standalone"


    class azure.mgmt.securityinsight.models.PackageModel(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[PackageProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[PackageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.PackageProperties(PackageBaseProperties):
        author: MetadataAuthor
        categories: MetadataCategories
        content_id: str
        content_kind: Union[str, PackageKind]
        content_product_id: str
        content_schema_version: str
        dependencies: MetadataDependencies
        description: str
        display_name: str
        first_publish_date: date
        icon: str
        is_deprecated: Union[str, Flag]
        is_featured: Union[str, Flag]
        is_new: Union[str, Flag]
        is_preview: Union[str, Flag]
        last_publish_date: date
        providers: list[str]
        publisher_display_name: str
        source: MetadataSource
        support: MetadataSupport
        threat_analysis_tactics: list[str]
        threat_analysis_techniques: list[str]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                author: Optional[MetadataAuthor] = ..., 
                categories: Optional[MetadataCategories] = ..., 
                content_id: Optional[str] = ..., 
                content_kind: Optional[Union[str, PackageKind]] = ..., 
                content_product_id: Optional[str] = ..., 
                content_schema_version: Optional[str] = ..., 
                dependencies: Optional[MetadataDependencies] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                first_publish_date: Optional[date] = ..., 
                icon: Optional[str] = ..., 
                is_deprecated: Optional[Union[str, Flag]] = ..., 
                is_featured: Optional[Union[str, Flag]] = ..., 
                is_new: Optional[Union[str, Flag]] = ..., 
                is_preview: Optional[Union[str, Flag]] = ..., 
                last_publish_date: Optional[date] = ..., 
                providers: Optional[list[str]] = ..., 
                publisher_display_name: Optional[str] = ..., 
                source: Optional[MetadataSource] = ..., 
                support: Optional[MetadataSupport] = ..., 
                threat_analysis_tactics: Optional[list[str]] = ..., 
                threat_analysis_techniques: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PermissionProviderScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESOURCE_GROUP = "ResourceGroup"
        SUBSCRIPTION = "Subscription"
        WORKSPACE = "Workspace"


    class azure.mgmt.securityinsight.models.Permissions(_Model):
        customs: Optional[list[PermissionsCustomsItem]]
        resource_provider: Optional[list[PermissionsResourceProviderItem]]

        @overload
        def __init__(
                self, 
                *, 
                customs: Optional[list[PermissionsCustomsItem]] = ..., 
                resource_provider: Optional[list[PermissionsResourceProviderItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PermissionsCustomsItem(Customs):
        description: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PermissionsResourceProviderItem(ResourceProvider):
        permissions_display_text: str
        provider: Union[str, ProviderName]
        provider_display_name: str
        required_permissions: RequiredPermissions
        scope: Union[str, PermissionProviderScope]

        @overload
        def __init__(
                self, 
                *, 
                permissions_display_text: Optional[str] = ..., 
                provider: Optional[Union[str, ProviderName]] = ..., 
                provider_display_name: Optional[str] = ..., 
                required_permissions: Optional[RequiredPermissions] = ..., 
                scope: Optional[Union[str, PermissionProviderScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PlaybookActionProperties(_Model):
        logic_app_resource_id: str
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                logic_app_resource_id: str, 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PollingFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONCE_AN_HOUR = "OnceAnHour"
        ONCE_A_DAY = "OnceADay"
        ONCE_A_MINUTE = "OnceAMinute"


    class azure.mgmt.securityinsight.models.PremiumMdtiDataConnectorDataTypes(_Model):
        connector: PremiumMdtiDataConnectorDataTypesConnector

        @overload
        def __init__(
                self, 
                *, 
                connector: PremiumMdtiDataConnectorDataTypesConnector
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PremiumMdtiDataConnectorDataTypesConnector(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PremiumMdtiDataConnectorProperties(DataConnectorTenantId):
        data_types: PremiumMdtiDataConnectorDataTypes
        lookback_period: datetime
        required_skus_present: Optional[bool]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                data_types: PremiumMdtiDataConnectorDataTypes, 
                lookback_period: datetime, 
                required_skus_present: Optional[bool] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PremiumMicrosoftDefenderForThreatIntelligence(DataConnector, discriminator='PremiumMicrosoftDefenderForThreatIntelligence'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.PREMIUM_MICROSOFT_DEFENDER_FOR_THREAT_INTELLIGENCE]
        name: str
        properties: Optional[PremiumMdtiDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[PremiumMdtiDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ProcessEntity(Entity, discriminator='Process'):
        id: str
        kind: Literal[EntityKind.PROCESS]
        name: str
        properties: Optional[ProcessEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProcessEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ProcessEntityProperties(EntityCommonProperties):
        account_entity_id: Optional[str]
        additional_data: dict[str, any]
        command_line: Optional[str]
        creation_time_utc: Optional[datetime]
        elevation_token: Optional[Union[str, ElevationToken]]
        friendly_name: str
        host_entity_id: Optional[str]
        host_logon_session_entity_id: Optional[str]
        image_file_entity_id: Optional[str]
        parent_process_entity_id: Optional[str]
        process_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                elevation_token: Optional[Union[str, ElevationToken]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ProductPackageModel(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[ProductPackageProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ProductPackageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ProductPackageProperties(_Model):
        author: Optional[MetadataAuthor]
        categories: Optional[MetadataCategories]
        content_id: Optional[str]
        content_kind: Optional[Union[str, PackageKind]]
        content_product_id: Optional[str]
        content_schema_version: Optional[str]
        dependencies: Optional[MetadataDependencies]
        description: Optional[str]
        display_name: Optional[str]
        first_publish_date: Optional[date]
        icon: Optional[str]
        installed_version: Optional[str]
        is_deprecated: Optional[Union[str, Flag]]
        is_featured: Optional[Union[str, Flag]]
        is_new: Optional[Union[str, Flag]]
        is_preview: Optional[Union[str, Flag]]
        last_publish_date: Optional[date]
        metadata_resource_id: Optional[str]
        packaged_content: Optional[Any]
        providers: Optional[list[str]]
        publisher_display_name: Optional[str]
        source: Optional[MetadataSource]
        support: Optional[MetadataSupport]
        threat_analysis_tactics: Optional[list[str]]
        threat_analysis_techniques: Optional[list[str]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                author: Optional[MetadataAuthor] = ..., 
                categories: Optional[MetadataCategories] = ..., 
                content_id: Optional[str] = ..., 
                content_kind: Optional[Union[str, PackageKind]] = ..., 
                content_product_id: Optional[str] = ..., 
                content_schema_version: Optional[str] = ..., 
                dependencies: Optional[MetadataDependencies] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                first_publish_date: Optional[date] = ..., 
                icon: Optional[str] = ..., 
                installed_version: Optional[str] = ..., 
                is_deprecated: Optional[Union[str, Flag]] = ..., 
                is_featured: Optional[Union[str, Flag]] = ..., 
                is_new: Optional[Union[str, Flag]] = ..., 
                is_preview: Optional[Union[str, Flag]] = ..., 
                last_publish_date: Optional[date] = ..., 
                metadata_resource_id: Optional[str] = ..., 
                packaged_content: Optional[Any] = ..., 
                providers: Optional[list[str]] = ..., 
                publisher_display_name: Optional[str] = ..., 
                source: Optional[MetadataSource] = ..., 
                support: Optional[MetadataSupport] = ..., 
                threat_analysis_tactics: Optional[list[str]] = ..., 
                threat_analysis_techniques: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ProductTemplateModel(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[ProductTemplateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ProductTemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ProductTemplateProperties(_Model):
        author: Optional[MetadataAuthor]
        categories: Optional[MetadataCategories]
        content_id: Optional[str]
        content_kind: Optional[Union[str, Kind]]
        content_product_id: Optional[str]
        content_schema_version: Optional[str]
        custom_version: Optional[str]
        dependencies: Optional[MetadataDependencies]
        display_name: Optional[str]
        first_publish_date: Optional[date]
        icon: Optional[str]
        is_deprecated: Optional[Union[str, Flag]]
        last_publish_date: Optional[date]
        package_id: Optional[str]
        package_kind: Optional[Union[str, PackageKind]]
        package_name: Optional[str]
        package_version: Optional[str]
        packaged_content: Optional[Any]
        preview_images: Optional[list[str]]
        preview_images_dark: Optional[list[str]]
        providers: Optional[list[str]]
        source: Optional[MetadataSource]
        support: Optional[MetadataSupport]
        threat_analysis_tactics: Optional[list[str]]
        threat_analysis_techniques: Optional[list[str]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                author: Optional[MetadataAuthor] = ..., 
                categories: Optional[MetadataCategories] = ..., 
                content_id: Optional[str] = ..., 
                content_kind: Optional[Union[str, Kind]] = ..., 
                content_product_id: Optional[str] = ..., 
                content_schema_version: Optional[str] = ..., 
                custom_version: Optional[str] = ..., 
                dependencies: Optional[MetadataDependencies] = ..., 
                display_name: Optional[str] = ..., 
                first_publish_date: Optional[date] = ..., 
                icon: Optional[str] = ..., 
                last_publish_date: Optional[date] = ..., 
                package_id: Optional[str] = ..., 
                package_kind: Optional[Union[str, PackageKind]] = ..., 
                package_name: Optional[str] = ..., 
                package_version: Optional[str] = ..., 
                packaged_content: Optional[Any] = ..., 
                preview_images: Optional[list[str]] = ..., 
                preview_images_dark: Optional[list[str]] = ..., 
                providers: Optional[list[str]] = ..., 
                source: Optional[MetadataSource] = ..., 
                support: Optional[MetadataSupport] = ..., 
                threat_analysis_tactics: Optional[list[str]] = ..., 
                threat_analysis_techniques: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PropertyArrayChangedConditionProperties(AutomationRuleCondition, discriminator='PropertyArrayChanged'):
        condition_properties: Optional[AutomationRulePropertyArrayChangedValuesCondition]
        condition_type: Literal[ConditionType.PROPERTY_ARRAY_CHANGED]

        @overload
        def __init__(
                self, 
                *, 
                condition_properties: Optional[AutomationRulePropertyArrayChangedValuesCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PropertyArrayConditionProperties(AutomationRuleCondition, discriminator='PropertyArray'):
        condition_properties: Optional[AutomationRulePropertyArrayValuesCondition]
        condition_type: Literal[ConditionType.PROPERTY_ARRAY]

        @overload
        def __init__(
                self, 
                *, 
                condition_properties: Optional[AutomationRulePropertyArrayValuesCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PropertyChangedConditionProperties(AutomationRuleCondition, discriminator='PropertyChanged'):
        condition_properties: Optional[AutomationRulePropertyValuesChangedCondition]
        condition_type: Literal[ConditionType.PROPERTY_CHANGED]

        @overload
        def __init__(
                self, 
                *, 
                condition_properties: Optional[AutomationRulePropertyValuesChangedCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PropertyConditionProperties(AutomationRuleCondition, discriminator='Property'):
        condition_properties: Optional[AutomationRulePropertyValuesCondition]
        condition_type: Literal[ConditionType.PROPERTY]

        @overload
        def __init__(
                self, 
                *, 
                condition_properties: Optional[AutomationRulePropertyValuesCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ProviderName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_AADIAM_DIAGNOSTIC_SETTINGS = "microsoft.aadiam/diagnosticSettings"
        MICROSOFT_AUTHORIZATION_POLICY_ASSIGNMENTS = "Microsoft.Authorization/policyAssignments"
        MICROSOFT_OPERATIONAL_INSIGHTS_SOLUTIONS = "Microsoft.OperationalInsights/solutions"
        MICROSOFT_OPERATIONAL_INSIGHTS_WORKSPACES = "Microsoft.OperationalInsights/workspaces"
        MICROSOFT_OPERATIONAL_INSIGHTS_WORKSPACES_DATASOURCES = "Microsoft.OperationalInsights/workspaces/datasources"
        MICROSOFT_OPERATIONAL_INSIGHTS_WORKSPACES_SHARED_KEYS = "Microsoft.OperationalInsights/workspaces/sharedKeys"


    class azure.mgmt.securityinsight.models.ProviderPermissionsScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESOURCE_GROUP = "ResourceGroup"
        SUBSCRIPTION = "Subscription"
        WORKSPACE = "Workspace"


    class azure.mgmt.securityinsight.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.securityinsight.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.securityinsight.models.PullRequest(_Model):
        state: Optional[Union[str, PullRequestState]]
        url: Optional[str]


    class azure.mgmt.securityinsight.models.PullRequestState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOSED = "Closed"
        OPEN = "Open"


    class azure.mgmt.securityinsight.models.PurviewAuditCheckRequirements(DataConnectorsCheckRequirements, discriminator='PurviewAudit'):
        kind: Literal[DataConnectorKind.PURVIEW_AUDIT]
        properties: Optional[PurviewAuditCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PurviewAuditCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.PurviewAuditCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PurviewAuditConnectorDataTypes(_Model):
        logs: PurviewAuditConnectorDataTypesLogs

        @overload
        def __init__(
                self, 
                *, 
                logs: PurviewAuditConnectorDataTypesLogs
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PurviewAuditConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.PurviewAuditDataConnector(DataConnector, discriminator='PurviewAudit'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.PURVIEW_AUDIT]
        name: str
        properties: Optional[PurviewAuditDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[PurviewAuditDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.PurviewAuditDataConnectorProperties(DataConnectorTenantId):
        connector_definition_name: Optional[str]
        data_types: PurviewAuditConnectorDataTypes
        dcr_config: Optional[DCRConfiguration]
        source_type: Optional[str]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                connector_definition_name: Optional[str] = ..., 
                data_types: PurviewAuditConnectorDataTypes, 
                dcr_config: Optional[DCRConfiguration] = ..., 
                source_type: Optional[str] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Query(_Model):
        condition: Optional[QueryCondition]
        max_page_size: Optional[int]
        min_page_size: Optional[int]
        sort_by: Optional[QuerySortBy]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[QueryCondition] = ..., 
                max_page_size: Optional[int] = ..., 
                min_page_size: Optional[int] = ..., 
                sort_by: Optional[QuerySortBy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.QueryCondition(_Model):
        clauses: list[ConditionClause]
        condition_connective: Optional[Union[str, Connective]]
        stix_object_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                clauses: list[ConditionClause], 
                condition_connective: Optional[Union[str, Connective]] = ..., 
                stix_object_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.QueryProperties(_Model):
        condition: Optional[ConditionProperties]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[ConditionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.QuerySortBy(_Model):
        direction: Optional[Union[str, SortingDirection]]
        field: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                direction: Optional[Union[str, SortingDirection]] = ..., 
                field: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Recommendation(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[RecommendationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[RecommendationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.RecommendationPatch(_Model):
        properties: Optional[RecommendationPatchProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RecommendationPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RecommendationPatchProperties(_Model):
        state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RecommendationProperties(_Model):
        additional_properties: Optional[dict[str, str]]
        creation_time_utc: datetime
        description: str
        last_evaluated_time_utc: datetime
        last_modified_time_utc: datetime
        recommendation_type_id: str
        resource_id: Optional[str]
        state: Union[str, State]
        suggestions: list[RecommendedSuggestion]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                additional_properties: Optional[dict[str, str]] = ..., 
                creation_time_utc: datetime, 
                description: str, 
                last_evaluated_time_utc: datetime, 
                last_modified_time_utc: datetime, 
                recommendation_type_id: str, 
                resource_id: Optional[str] = ..., 
                state: Union[str, State], 
                suggestions: list[RecommendedSuggestion], 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RecommendedSuggestion(_Model):
        action: str
        additional_properties: Optional[dict[str, str]]
        description: str
        suggestion_type_id: str
        title: str

        @overload
        def __init__(
                self, 
                *, 
                action: str, 
                additional_properties: Optional[dict[str, str]] = ..., 
                description: str, 
                suggestion_type_id: str, 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ReevaluateResponse(_Model):
        last_evaluated_time_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                last_evaluated_time_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.securityinsight.models.RegistryKeyEntity(Entity, discriminator='RegistryKey'):
        id: str
        kind: Literal[EntityKind.REGISTRY_KEY]
        name: str
        properties: Optional[RegistryKeyEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RegistryKeyEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.RegistryKeyEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        hive: Optional[Union[str, RegistryHive]]
        key: Optional[str]


    class azure.mgmt.securityinsight.models.RegistryValueEntity(Entity, discriminator='RegistryValue'):
        id: str
        kind: Literal[EntityKind.REGISTRY_VALUE]
        name: str
        properties: Optional[RegistryValueEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RegistryValueEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.RegistryValueEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        key_entity_id: Optional[str]
        value_data: Optional[str]
        value_name: Optional[str]
        value_type: Optional[Union[str, RegistryValueKind]]


    class azure.mgmt.securityinsight.models.RegistryValueKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY = "Binary"
        D_WORD = "DWord"
        EXPAND_STRING = "ExpandString"
        MULTI_STRING = "MultiString"
        NONE = "None"
        Q_WORD = "QWord"
        STRING = "String"
        UNKNOWN = "Unknown"


    class azure.mgmt.securityinsight.models.Relation(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[RelationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[RelationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.RelationProperties(_Model):
        related_resource_id: str
        related_resource_kind: Optional[str]
        related_resource_name: Optional[str]
        related_resource_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                related_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Relationship(TIObject, discriminator='Relationship'):
        id: str
        kind: Literal[TIObjectKind.RELATIONSHIP]
        name: str
        properties: TIObjectCommonProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TIObjectCommonProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.RelationshipHint(_Model):
        field_name: Optional[str]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                field_name: Optional[str] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Repo(_Model):
        branches: Optional[list[str]]
        full_name: Optional[str]
        installation_id: Optional[int]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                branches: Optional[list[str]] = ..., 
                full_name: Optional[str] = ..., 
                installation_id: Optional[int] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RepoType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DEV_OPS = "AzureDevOps"
        GITHUB = "Github"


    class azure.mgmt.securityinsight.models.Repository(_Model):
        branch: str
        deployment_logs_url: Optional[str]
        display_url: Optional[str]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                branch: str, 
                display_url: Optional[str] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RepositoryAccess(_Model):
        client_id: Optional[str]
        code: Optional[str]
        installation_id: Optional[str]
        kind: Union[str, RepositoryAccessKind]
        state: Optional[str]
        token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                code: Optional[str] = ..., 
                installation_id: Optional[str] = ..., 
                kind: Union[str, RepositoryAccessKind], 
                state: Optional[str] = ..., 
                token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RepositoryAccessKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP = "App"
        O_AUTH = "OAuth"
        PAT = "PAT"


    class azure.mgmt.securityinsight.models.RepositoryAccessObject(_Model):
        repository_access: RepositoryAccess

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                repository_access: RepositoryAccess
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.RepositoryAccessProperties(_Model):
        properties: RepositoryAccessObject

        @overload
        def __init__(
                self, 
                *, 
                properties: RepositoryAccessObject
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RepositoryResourceInfo(_Model):
        azure_dev_ops_resource_info: Optional[AzureDevOpsResourceInfo]
        git_hub_resource_info: Optional[GitHubResourceInfo]
        webhook: Optional[Webhook]

        @overload
        def __init__(
                self, 
                *, 
                webhook: Optional[Webhook] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RequiredPermissions(_Model):
        action: Optional[bool]
        delete: Optional[bool]
        read: Optional[bool]
        write: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[bool] = ..., 
                delete: Optional[bool] = ..., 
                read: Optional[bool] = ..., 
                write: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.securityinsight.models.ResourceProvider(_Model):
        permissions_display_text: Optional[str]
        provider: Optional[Union[str, ProviderName]]
        provider_display_name: Optional[str]
        required_permissions: Optional[RequiredPermissions]
        scope: Optional[Union[str, PermissionProviderScope]]

        @overload
        def __init__(
                self, 
                *, 
                permissions_display_text: Optional[str] = ..., 
                provider: Optional[Union[str, ProviderName]] = ..., 
                provider_display_name: Optional[str] = ..., 
                required_permissions: Optional[RequiredPermissions] = ..., 
                scope: Optional[Union[str, PermissionProviderScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ResourceProviderRequiredPermissions(_Model):
        action: Optional[bool]
        delete: Optional[bool]
        read: Optional[bool]
        write: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[bool] = ..., 
                delete: Optional[bool] = ..., 
                read: Optional[bool] = ..., 
                write: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ResourceWithEtag(Resource):
        etag: Optional[str]
        id: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RestApiPollerDataConnector(DataConnector, discriminator='RestApiPoller'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.REST_API_POLLER]
        name: str
        properties: Optional[RestApiPollerDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[RestApiPollerDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.RestApiPollerDataConnectorProperties(_Model):
        add_on_attributes: Optional[dict[str, str]]
        auth: CcpAuthConfig
        connector_definition_name: str
        data_type: Optional[str]
        dcr_config: Optional[DCRConfiguration]
        is_active: Optional[bool]
        paging: Optional[RestApiPollerRequestPagingConfig]
        request: RestApiPollerRequestConfig
        response: Optional[CcpResponseConfig]

        @overload
        def __init__(
                self, 
                *, 
                add_on_attributes: Optional[dict[str, str]] = ..., 
                auth: CcpAuthConfig, 
                connector_definition_name: str, 
                data_type: Optional[str] = ..., 
                dcr_config: Optional[DCRConfiguration] = ..., 
                is_active: Optional[bool] = ..., 
                paging: Optional[RestApiPollerRequestPagingConfig] = ..., 
                request: RestApiPollerRequestConfig, 
                response: Optional[CcpResponseConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RestApiPollerRequestConfig(_Model):
        api_endpoint: str
        end_time_attribute_name: Optional[str]
        headers: Optional[dict[str, str]]
        http_method: Optional[Union[str, HttpMethodVerb]]
        is_post_payload_json: Optional[bool]
        query_parameters: Optional[dict[str, Any]]
        query_parameters_template: Optional[str]
        query_time_format: Optional[str]
        query_time_interval_attribute_name: Optional[str]
        query_time_interval_delimiter: Optional[str]
        query_time_interval_prepend: Optional[str]
        query_window_in_min: Optional[int]
        rate_limit_qps: Optional[int]
        retry_count: Optional[int]
        start_time_attribute_name: Optional[str]
        timeout_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                api_endpoint: str, 
                end_time_attribute_name: Optional[str] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                http_method: Optional[Union[str, HttpMethodVerb]] = ..., 
                is_post_payload_json: Optional[bool] = ..., 
                query_parameters: Optional[dict[str, Any]] = ..., 
                query_parameters_template: Optional[str] = ..., 
                query_time_format: Optional[str] = ..., 
                query_time_interval_attribute_name: Optional[str] = ..., 
                query_time_interval_delimiter: Optional[str] = ..., 
                query_time_interval_prepend: Optional[str] = ..., 
                query_window_in_min: Optional[int] = ..., 
                rate_limit_qps: Optional[int] = ..., 
                retry_count: Optional[int] = ..., 
                start_time_attribute_name: Optional[str] = ..., 
                timeout_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RestApiPollerRequestPagingConfig(_Model):
        page_size: Optional[int]
        page_size_parameter_name: Optional[str]
        paging_type: Union[str, RestApiPollerRequestPagingKind]

        @overload
        def __init__(
                self, 
                *, 
                page_size: Optional[int] = ..., 
                page_size_parameter_name: Optional[str] = ..., 
                paging_type: Union[str, RestApiPollerRequestPagingKind]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.RestApiPollerRequestPagingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT_BASED_PAGING = "CountBasedPaging"
        LINK_HEADER = "LinkHeader"
        NEXT_PAGE_TOKEN = "NextPageToken"
        NEXT_PAGE_URL = "NextPageUrl"
        OFFSET = "Offset"
        PERSISTENT_LINK_HEADER = "PersistentLinkHeader"
        PERSISTENT_TOKEN = "PersistentToken"


    class azure.mgmt.securityinsight.models.SampleQueries(_Model):
        description: Optional[str]
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SapSolutionUsageStatistic(BillingStatistic, discriminator='SapSolutionUsage'):
        etag: str
        id: str
        kind: Literal[BillingStatisticKind.SAP_SOLUTION_USAGE]
        name: str
        properties: Optional[SapSolutionUsageStatisticProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SapSolutionUsageStatisticProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.SapSolutionUsageStatisticProperties(_Model):
        active_system_id_count: Optional[int]


    class azure.mgmt.securityinsight.models.ScheduledAlertRule(AlertRule, discriminator='Scheduled'):
        etag: str
        id: str
        kind: Literal[AlertRuleKind.SCHEDULED]
        name: str
        properties: Optional[ScheduledAlertRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ScheduledAlertRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ScheduledAlertRuleCommonProperties(_Model):
        alert_details_override: Optional[AlertDetailsOverride]
        custom_details: Optional[dict[str, str]]
        entity_mappings: Optional[list[EntityMapping]]
        event_grouping_settings: Optional[EventGroupingSettings]
        query: Optional[str]
        query_frequency: Optional[timedelta]
        query_period: Optional[timedelta]
        sentinel_entities_mappings: Optional[list[SentinelEntityMapping]]
        severity: Optional[Union[str, AlertSeverity]]
        trigger_operator: Optional[Union[str, TriggerOperator]]
        trigger_threshold: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                custom_details: Optional[dict[str, str]] = ..., 
                entity_mappings: Optional[list[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                query: Optional[str] = ..., 
                query_frequency: Optional[timedelta] = ..., 
                query_period: Optional[timedelta] = ..., 
                sentinel_entities_mappings: Optional[list[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                trigger_operator: Optional[Union[str, TriggerOperator]] = ..., 
                trigger_threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ScheduledAlertRuleProperties(ScheduledAlertRuleCommonProperties):
        alert_details_override: AlertDetailsOverride
        alert_rule_template_name: Optional[str]
        custom_details: dict[str, str]
        description: Optional[str]
        display_name: str
        enabled: bool
        entity_mappings: list[EntityMapping]
        event_grouping_settings: EventGroupingSettings
        incident_configuration: Optional[IncidentConfiguration]
        last_modified_utc: Optional[datetime]
        query: str
        query_frequency: timedelta
        query_period: timedelta
        sentinel_entities_mappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        sub_techniques: Optional[list[str]]
        suppression_duration: timedelta
        suppression_enabled: bool
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]
        template_version: Optional[str]
        trigger_operator: Union[str, TriggerOperator]
        trigger_threshold: int

        @overload
        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                alert_rule_template_name: Optional[str] = ..., 
                custom_details: Optional[dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                enabled: bool, 
                entity_mappings: Optional[list[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                incident_configuration: Optional[IncidentConfiguration] = ..., 
                query: Optional[str] = ..., 
                query_frequency: Optional[timedelta] = ..., 
                query_period: Optional[timedelta] = ..., 
                sentinel_entities_mappings: Optional[list[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                sub_techniques: Optional[list[str]] = ..., 
                suppression_duration: timedelta, 
                suppression_enabled: bool, 
                tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[list[str]] = ..., 
                template_version: Optional[str] = ..., 
                trigger_operator: Optional[Union[str, TriggerOperator]] = ..., 
                trigger_threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ScheduledAlertRuleTemplate(AlertRuleTemplate, discriminator='Scheduled'):
        id: str
        kind: Literal[AlertRuleKind.SCHEDULED]
        name: str
        properties: Optional[ScheduledAlertRuleTemplateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScheduledAlertRuleTemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ScheduledAlertRuleTemplateProperties(_Model):
        alert_details_override: Optional[AlertDetailsOverride]
        alert_rules_created_by_template_count: Optional[int]
        created_date_utc: Optional[datetime]
        custom_details: Optional[dict[str, str]]
        description: Optional[str]
        display_name: Optional[str]
        entity_mappings: Optional[list[EntityMapping]]
        event_grouping_settings: Optional[EventGroupingSettings]
        last_updated_date_utc: Optional[datetime]
        query: Optional[str]
        query_frequency: Optional[timedelta]
        query_period: Optional[timedelta]
        required_data_connectors: Optional[list[AlertRuleTemplateDataSource]]
        sentinel_entities_mappings: Optional[list[SentinelEntityMapping]]
        severity: Optional[Union[str, AlertSeverity]]
        status: Optional[Union[str, TemplateStatus]]
        sub_techniques: Optional[list[str]]
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]
        trigger_operator: Optional[Union[str, TriggerOperator]]
        trigger_threshold: Optional[int]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                alert_details_override: Optional[AlertDetailsOverride] = ..., 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                custom_details: Optional[dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                entity_mappings: Optional[list[EntityMapping]] = ..., 
                event_grouping_settings: Optional[EventGroupingSettings] = ..., 
                query: Optional[str] = ..., 
                query_frequency: Optional[timedelta] = ..., 
                query_period: Optional[timedelta] = ..., 
                required_data_connectors: Optional[list[AlertRuleTemplateDataSource]] = ..., 
                sentinel_entities_mappings: Optional[list[SentinelEntityMapping]] = ..., 
                severity: Optional[Union[str, AlertSeverity]] = ..., 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                sub_techniques: Optional[list[str]] = ..., 
                tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[list[str]] = ..., 
                trigger_operator: Optional[Union[str, TriggerOperator]] = ..., 
                trigger_threshold: Optional[int] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SecurityAlert(Entity, discriminator='SecurityAlert'):
        id: str
        kind: Literal[EntityKind.SECURITY_ALERT]
        name: str
        properties: Optional[SecurityAlertProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityAlertProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.SecurityAlertProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        alert_display_name: Optional[str]
        alert_link: Optional[str]
        alert_type: Optional[str]
        compromised_entity: Optional[str]
        confidence_level: Optional[Union[str, ConfidenceLevel]]
        confidence_reasons: Optional[list[SecurityAlertPropertiesConfidenceReasonsItem]]
        confidence_score: Optional[float]
        confidence_score_status: Optional[Union[str, ConfidenceScoreStatus]]
        description: Optional[str]
        end_time_utc: Optional[datetime]
        friendly_name: str
        intent: Optional[Union[str, KillChainIntent]]
        processing_end_time: Optional[datetime]
        product_component_name: Optional[str]
        product_name: Optional[str]
        product_version: Optional[str]
        provider_alert_id: Optional[str]
        remediation_steps: Optional[list[str]]
        resource_identifiers: Optional[list[Any]]
        severity: Optional[Union[str, AlertSeverity]]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, AlertStatus]]
        system_alert_id: Optional[str]
        tactics: Optional[list[Union[str, AttackTactic]]]
        time_generated: Optional[datetime]
        vendor_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                severity: Optional[Union[str, AlertSeverity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SecurityAlertPropertiesConfidenceReasonsItem(_Model):
        reason: Optional[str]
        reason_type: Optional[str]


    class azure.mgmt.securityinsight.models.SecurityAlertTimelineItem(EntityTimelineItem, discriminator='SecurityAlert'):
        alert_type: str
        azure_resource_id: str
        description: Optional[str]
        display_name: str
        end_time_utc: datetime
        intent: Optional[Union[str, KillChainIntent]]
        kind: Literal[EntityTimelineKind.SECURITY_ALERT]
        product_name: Optional[str]
        severity: Union[str, AlertSeverity]
        start_time_utc: datetime
        techniques: Optional[list[str]]
        time_generated: datetime

        @overload
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
                techniques: Optional[list[str]] = ..., 
                time_generated: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SecurityGroupEntity(Entity, discriminator='SecurityGroup'):
        id: str
        kind: Literal[EntityKind.SECURITY_GROUP]
        name: str
        properties: Optional[SecurityGroupEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityGroupEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.SecurityGroupEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        distinguished_name: Optional[str]
        friendly_name: str
        object_guid: Optional[str]
        sid: Optional[str]


    class azure.mgmt.securityinsight.models.SecurityMLAnalyticsSetting(ProxyResource):
        etag: Optional[str]
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SecurityMLAnalyticsSettingsDataSource(_Model):
        connector_id: Optional[str]
        data_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                connector_id: Optional[str] = ..., 
                data_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SecurityMLAnalyticsSettingsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANOMALY = "Anomaly"


    class azure.mgmt.securityinsight.models.SentinelEntityMapping(_Model):
        column_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                column_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SentinelOnboardingState(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[SentinelOnboardingStateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[SentinelOnboardingStateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.SentinelOnboardingStateProperties(_Model):
        customer_managed_key: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_key: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SentinelOnboardingStatesList(_Model):
        value: list[SentinelOnboardingState]

        @overload
        def __init__(
                self, 
                *, 
                value: list[SentinelOnboardingState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ServicePrincipal(_Model):
        app_id: Optional[str]
        credentials_expire_on: Optional[datetime]
        id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                credentials_expire_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SessionAuthModel(CcpAuthConfig, discriminator='Session'):
        headers: Optional[dict[str, str]]
        is_post_payload_json: Optional[bool]
        password: dict[str, str]
        query_parameters: Optional[dict[str, Any]]
        session_id_name: Optional[str]
        session_login_request_uri: Optional[str]
        session_timeout_in_minutes: Optional[int]
        type: Literal[CcpAuthType.SESSION]
        user_name: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[dict[str, str]] = ..., 
                is_post_payload_json: Optional[bool] = ..., 
                password: dict[str, str], 
                query_parameters: Optional[dict[str, Any]] = ..., 
                session_id_name: Optional[str] = ..., 
                session_login_request_uri: Optional[str] = ..., 
                session_timeout_in_minutes: Optional[int] = ..., 
                user_name: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANOMALIES = "Anomalies"
        ENTITY_ANALYTICS = "EntityAnalytics"
        EYES_ON = "EyesOn"
        UEBA = "Ueba"


    class azure.mgmt.securityinsight.models.SettingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPYABLE_LABEL = "CopyableLabel"
        INFO_MESSAGE = "InfoMessage"
        INSTRUCTION_STEPS_GROUP = "InstructionStepsGroup"


    class azure.mgmt.securityinsight.models.Settings(ProxyResource):
        etag: Optional[str]
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SettingsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLIGHTING = "Flighting"
        PRODUCTION = "Production"


    class azure.mgmt.securityinsight.models.SortingDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "ASC"
        DESC = "DESC"


    class azure.mgmt.securityinsight.models.SourceControl(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: SourceControlProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: SourceControlProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.SourceControlProperties(_Model):
        content_types: list[Union[str, ContentType]]
        description: Optional[str]
        display_name: str
        id: Optional[str]
        last_deployment_info: Optional[DeploymentInfo]
        pull_request: Optional[PullRequest]
        repo_type: Union[str, RepoType]
        repository: Repository
        repository_access: Optional[RepositoryAccess]
        repository_resource_info: Optional[RepositoryResourceInfo]
        service_principal: Optional[ServicePrincipal]
        version: Optional[Union[str, Version]]
        workload_identity_federation: Optional[WorkloadIdentityFederation]

        @overload
        def __init__(
                self, 
                *, 
                content_types: list[Union[str, ContentType]], 
                description: Optional[str] = ..., 
                display_name: str, 
                repo_type: Union[str, RepoType], 
                repository: Repository, 
                repository_access: Optional[RepositoryAccess] = ..., 
                repository_resource_info: Optional[RepositoryResourceInfo] = ..., 
                service_principal: Optional[ServicePrincipal] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.SourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMUNITY = "Community"
        LOCAL_WORKSPACE = "LocalWorkspace"
        SOLUTION = "Solution"
        SOURCE_REPOSITORY = "SourceRepository"


    class azure.mgmt.securityinsight.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_STORAGE = "AzureStorage"
        LOCAL = "Local"


    class azure.mgmt.securityinsight.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        COMPLETED_BY_SYSTEM = "CompletedBySystem"
        COMPLETED_BY_USER = "CompletedByUser"
        DISMISSED = "Dismissed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.securityinsight.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        APPROVED = "Approved"
        BACKLOG = "Backlog"
        CLOSED = "Closed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NEW = "New"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.securityinsight.models.SubmissionMailEntity(Entity, discriminator='SubmissionMail'):
        id: str
        kind: Literal[EntityKind.SUBMISSION_MAIL]
        name: str
        properties: Optional[SubmissionMailEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubmissionMailEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.SubmissionMailEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        network_message_id: Optional[str]
        recipient: Optional[str]
        report_type: Optional[str]
        sender: Optional[str]
        sender_ip: Optional[str]
        subject: Optional[str]
        submission_date: Optional[datetime]
        submission_id: Optional[str]
        submitter: Optional[str]
        timestamp: Optional[datetime]


    class azure.mgmt.securityinsight.models.SupportTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMUNITY = "Community"
        MICROSOFT = "Microsoft"
        PARTNER = "Partner"


    class azure.mgmt.securityinsight.models.SystemData(_Model):
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


    class azure.mgmt.securityinsight.models.TICheckRequirements(DataConnectorsCheckRequirements, discriminator='ThreatIntelligence'):
        kind: Literal[DataConnectorKind.THREAT_INTELLIGENCE]
        properties: Optional[TICheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TICheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.TICheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TIDataConnector(DataConnector, discriminator='ThreatIntelligence'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.THREAT_INTELLIGENCE]
        name: str
        properties: Optional[TIDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[TIDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.TIDataConnectorDataTypes(_Model):
        indicators: TIDataConnectorDataTypesIndicators

        @overload
        def __init__(
                self, 
                *, 
                indicators: TIDataConnectorDataTypesIndicators
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TIDataConnectorDataTypesIndicators(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TIDataConnectorProperties(DataConnectorTenantId):
        data_types: TIDataConnectorDataTypes
        tenant_id: str
        tip_lookback_period: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                data_types: TIDataConnectorDataTypes, 
                tenant_id: str, 
                tip_lookback_period: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TIObject(Resource):
        id: str
        kind: str
        name: str
        properties: Optional[TIObjectCommonProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                properties: Optional[TIObjectCommonProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.TIObjectCommonProperties(_Model):
        created_by: Optional[UserInfo]
        data: Optional[dict[str, Any]]
        first_ingested_time_utc: Optional[datetime]
        ingestion_rules_version: Optional[str]
        last_ingested_time_utc: Optional[datetime]
        last_modified_by: Optional[UserInfo]
        last_update_method: Optional[str]
        last_updated_date_time_utc: Optional[datetime]
        relationship_hints: Optional[list[RelationshipHint]]
        source: Optional[str]


    class azure.mgmt.securityinsight.models.TIObjectKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTACK_PATTERN = "AttackPattern"
        IDENTITY = "Identity"
        INDICATOR = "Indicator"
        RELATIONSHIP = "Relationship"
        THREAT_ACTOR = "ThreatActor"


    class azure.mgmt.securityinsight.models.TeamInformation(_Model):
        description: Optional[str]
        name: Optional[str]
        primary_channel_url: Optional[str]
        team_creation_time_utc: Optional[datetime]
        team_id: Optional[str]


    class azure.mgmt.securityinsight.models.TemplateModel(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[TemplateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[TemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.TemplateProperties(_Model):
        author: Optional[MetadataAuthor]
        categories: Optional[MetadataCategories]
        content_id: Optional[str]
        content_kind: Optional[Union[str, Kind]]
        content_product_id: Optional[str]
        content_schema_version: Optional[str]
        custom_version: Optional[str]
        dependant_templates: Optional[list[TemplateProperties]]
        dependencies: Optional[MetadataDependencies]
        display_name: Optional[str]
        first_publish_date: Optional[date]
        icon: Optional[str]
        is_deprecated: Optional[Union[str, Flag]]
        last_publish_date: Optional[date]
        main_template: Optional[Any]
        package_id: Optional[str]
        package_kind: Optional[Union[str, PackageKind]]
        package_name: Optional[str]
        package_version: Optional[str]
        preview_images: Optional[list[str]]
        preview_images_dark: Optional[list[str]]
        providers: Optional[list[str]]
        source: Optional[MetadataSource]
        support: Optional[MetadataSupport]
        threat_analysis_tactics: Optional[list[str]]
        threat_analysis_techniques: Optional[list[str]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                author: Optional[MetadataAuthor] = ..., 
                categories: Optional[MetadataCategories] = ..., 
                content_id: Optional[str] = ..., 
                content_kind: Optional[Union[str, Kind]] = ..., 
                content_product_id: Optional[str] = ..., 
                content_schema_version: Optional[str] = ..., 
                custom_version: Optional[str] = ..., 
                dependencies: Optional[MetadataDependencies] = ..., 
                display_name: Optional[str] = ..., 
                first_publish_date: Optional[date] = ..., 
                icon: Optional[str] = ..., 
                last_publish_date: Optional[date] = ..., 
                main_template: Optional[Any] = ..., 
                package_id: Optional[str] = ..., 
                package_kind: Optional[Union[str, PackageKind]] = ..., 
                package_name: Optional[str] = ..., 
                package_version: Optional[str] = ..., 
                preview_images: Optional[list[str]] = ..., 
                preview_images_dark: Optional[list[str]] = ..., 
                providers: Optional[list[str]] = ..., 
                source: Optional[MetadataSource] = ..., 
                support: Optional[MetadataSupport] = ..., 
                threat_analysis_tactics: Optional[list[str]] = ..., 
                threat_analysis_techniques: Optional[list[str]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TemplateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        INSTALLED = "Installed"
        NOT_AVAILABLE = "NotAvailable"


    class azure.mgmt.securityinsight.models.ThreatActor(TIObject, discriminator='ThreatActor'):
        id: str
        kind: Literal[TIObjectKind.THREAT_ACTOR]
        name: str
        properties: TIObjectCommonProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TIObjectCommonProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligence(_Model):
        confidence: Optional[float]
        provider_name: Optional[str]
        report_link: Optional[str]
        threat_description: Optional[str]
        threat_name: Optional[str]
        threat_type: Optional[str]


    class azure.mgmt.securityinsight.models.ThreatIntelligenceAlertRule(AlertRule, discriminator='ThreatIntelligence'):
        etag: str
        id: str
        kind: Literal[AlertRuleKind.THREAT_INTELLIGENCE]
        name: str
        properties: Optional[ThreatIntelligenceAlertRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ThreatIntelligenceAlertRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceAlertRuleProperties(_Model):
        alert_rule_template_name: str
        description: Optional[str]
        display_name: Optional[str]
        enabled: bool
        last_modified_utc: Optional[datetime]
        severity: Optional[Union[str, AlertSeverity]]
        sub_techniques: Optional[list[str]]
        tactics: Optional[list[Union[str, AttackTactic]]]
        techniques: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                alert_rule_template_name: str, 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceAlertRuleTemplate(AlertRuleTemplate, discriminator='ThreatIntelligence'):
        id: str
        kind: Literal[AlertRuleKind.THREAT_INTELLIGENCE]
        name: str
        properties: Optional[ThreatIntelligenceAlertRuleTemplateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ThreatIntelligenceAlertRuleTemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


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

        @overload
        def __init__(
                self, 
                *, 
                alert_rules_created_by_template_count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                required_data_connectors: Optional[list[AlertRuleTemplateDataSource]] = ..., 
                severity: Union[str, AlertSeverity], 
                status: Optional[Union[str, TemplateStatus]] = ..., 
                tactics: Optional[list[Union[str, AttackTactic]]] = ..., 
                techniques: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceAppendTags(_Model):
        threat_intelligence_tags: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                threat_intelligence_tags: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceCount(_Model):
        count: int


    class azure.mgmt.securityinsight.models.ThreatIntelligenceExternalReference(_Model):
        description: Optional[str]
        external_id: Optional[str]
        hashes: Optional[dict[str, str]]
        source_name: Optional[str]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                external_id: Optional[str] = ..., 
                hashes: Optional[dict[str, str]] = ..., 
                source_name: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceFilteringCriteria(_Model):
        ids: Optional[list[str]]
        include_disabled: Optional[bool]
        keywords: Optional[list[str]]
        max_confidence: Optional[int]
        max_valid_until: Optional[str]
        min_confidence: Optional[int]
        min_valid_until: Optional[str]
        page_size: Optional[int]
        pattern_types: Optional[list[str]]
        skip_token: Optional[str]
        sort_by: Optional[list[ThreatIntelligenceSortingCriteria]]
        sources: Optional[list[str]]
        threat_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                ids: Optional[list[str]] = ..., 
                include_disabled: Optional[bool] = ..., 
                keywords: Optional[list[str]] = ..., 
                max_confidence: Optional[int] = ..., 
                max_valid_until: Optional[str] = ..., 
                min_confidence: Optional[int] = ..., 
                min_valid_until: Optional[str] = ..., 
                page_size: Optional[int] = ..., 
                pattern_types: Optional[list[str]] = ..., 
                skip_token: Optional[str] = ..., 
                sort_by: Optional[list[ThreatIntelligenceSortingCriteria]] = ..., 
                sources: Optional[list[str]] = ..., 
                threat_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceGranularMarkingModel(_Model):
        language: Optional[str]
        marking_ref: Optional[int]
        selectors: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                marking_ref: Optional[int] = ..., 
                selectors: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceIndicatorModel(ThreatIntelligenceInformation, discriminator='indicator'):
        etag: str
        id: str
        kind: Literal[ThreatIntelligenceResourceKindEnum.INDICATOR]
        name: str
        properties: Optional[ThreatIntelligenceIndicatorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ThreatIntelligenceIndicatorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceIndicatorProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        confidence: Optional[int]
        created: Optional[str]
        created_by_ref: Optional[str]
        defanged: Optional[bool]
        description: Optional[str]
        display_name: Optional[str]
        extensions: Optional[dict[str, Any]]
        external_id: Optional[str]
        external_last_updated_time_utc: Optional[str]
        external_references: Optional[list[ThreatIntelligenceExternalReference]]
        friendly_name: str
        granular_markings: Optional[list[ThreatIntelligenceGranularMarkingModel]]
        indicator_types: Optional[list[str]]
        kill_chain_phases: Optional[list[ThreatIntelligenceKillChainPhase]]
        labels: Optional[list[str]]
        language: Optional[str]
        last_updated_time_utc: Optional[str]
        modified: Optional[str]
        object_marking_refs: Optional[list[str]]
        parsed_pattern: Optional[list[ThreatIntelligenceParsedPattern]]
        pattern: Optional[str]
        pattern_type: Optional[str]
        pattern_version: Optional[str]
        revoked: Optional[bool]
        source: Optional[str]
        threat_intelligence_tags: Optional[list[str]]
        threat_types: Optional[list[str]]
        valid_from: Optional[str]
        valid_until: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[int] = ..., 
                created: Optional[str] = ..., 
                created_by_ref: Optional[str] = ..., 
                defanged: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                extensions: Optional[dict[str, Any]] = ..., 
                external_id: Optional[str] = ..., 
                external_last_updated_time_utc: Optional[str] = ..., 
                external_references: Optional[list[ThreatIntelligenceExternalReference]] = ..., 
                granular_markings: Optional[list[ThreatIntelligenceGranularMarkingModel]] = ..., 
                indicator_types: Optional[list[str]] = ..., 
                kill_chain_phases: Optional[list[ThreatIntelligenceKillChainPhase]] = ..., 
                labels: Optional[list[str]] = ..., 
                language: Optional[str] = ..., 
                last_updated_time_utc: Optional[str] = ..., 
                modified: Optional[str] = ..., 
                object_marking_refs: Optional[list[str]] = ..., 
                parsed_pattern: Optional[list[ThreatIntelligenceParsedPattern]] = ..., 
                pattern: Optional[str] = ..., 
                pattern_type: Optional[str] = ..., 
                pattern_version: Optional[str] = ..., 
                revoked: Optional[bool] = ..., 
                source: Optional[str] = ..., 
                threat_intelligence_tags: Optional[list[str]] = ..., 
                threat_types: Optional[list[str]] = ..., 
                valid_from: Optional[str] = ..., 
                valid_until: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceInformation(ProxyResource):
        etag: Optional[str]
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceKillChainPhase(_Model):
        kill_chain_name: Optional[str]
        phase_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kill_chain_name: Optional[str] = ..., 
                phase_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceMetric(_Model):
        last_updated_time_utc: Optional[str]
        pattern_type_metrics: Optional[list[ThreatIntelligenceMetricEntity]]
        source_metrics: Optional[list[ThreatIntelligenceMetricEntity]]
        threat_type_metrics: Optional[list[ThreatIntelligenceMetricEntity]]

        @overload
        def __init__(
                self, 
                *, 
                last_updated_time_utc: Optional[str] = ..., 
                pattern_type_metrics: Optional[list[ThreatIntelligenceMetricEntity]] = ..., 
                source_metrics: Optional[list[ThreatIntelligenceMetricEntity]] = ..., 
                threat_type_metrics: Optional[list[ThreatIntelligenceMetricEntity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceMetricEntity(_Model):
        metric_name: Optional[str]
        metric_value: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                metric_name: Optional[str] = ..., 
                metric_value: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceMetrics(_Model):
        properties: Optional[ThreatIntelligenceMetric]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ThreatIntelligenceMetric] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceMetricsList(_Model):
        value: list[ThreatIntelligenceMetrics]

        @overload
        def __init__(
                self, 
                *, 
                value: list[ThreatIntelligenceMetrics]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceParsedPattern(_Model):
        pattern_type_key: Optional[str]
        pattern_type_values: Optional[list[ThreatIntelligenceParsedPatternTypeValue]]

        @overload
        def __init__(
                self, 
                *, 
                pattern_type_key: Optional[str] = ..., 
                pattern_type_values: Optional[list[ThreatIntelligenceParsedPatternTypeValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceParsedPatternTypeValue(_Model):
        value: Optional[str]
        value_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ..., 
                value_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceResourceKindEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INDICATOR = "indicator"


    class azure.mgmt.securityinsight.models.ThreatIntelligenceSortingCriteria(_Model):
        item_key: Optional[str]
        sort_order: Optional[Union[str, ThreatIntelligenceSortingCriteriaEnum]]

        @overload
        def __init__(
                self, 
                *, 
                item_key: Optional[str] = ..., 
                sort_order: Optional[Union[str, ThreatIntelligenceSortingCriteriaEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ThreatIntelligenceSortingCriteriaEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCENDING = "ascending"
        DESCENDING = "descending"
        UNSORTED = "unsorted"


    class azure.mgmt.securityinsight.models.TiTaxiiCheckRequirements(DataConnectorsCheckRequirements, discriminator='ThreatIntelligenceTaxii'):
        kind: Literal[DataConnectorKind.THREAT_INTELLIGENCE_TAXII]
        properties: Optional[TiTaxiiCheckRequirementsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TiTaxiiCheckRequirementsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.TiTaxiiCheckRequirementsProperties(DataConnectorTenantId):
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TiTaxiiDataConnector(DataConnector, discriminator='ThreatIntelligenceTaxii'):
        etag: str
        id: str
        kind: Literal[DataConnectorKind.THREAT_INTELLIGENCE_TAXII]
        name: str
        properties: Optional[TiTaxiiDataConnectorProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[TiTaxiiDataConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.TiTaxiiDataConnectorDataTypes(_Model):
        taxii_client: TiTaxiiDataConnectorDataTypesTaxiiClient

        @overload
        def __init__(
                self, 
                *, 
                taxii_client: TiTaxiiDataConnectorDataTypesTaxiiClient
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TiTaxiiDataConnectorDataTypesTaxiiClient(DataConnectorDataTypeCommon):
        state: Union[str, DataTypeState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, DataTypeState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TiTaxiiDataConnectorProperties(DataConnectorTenantId):
        collection_id: Optional[str]
        data_types: TiTaxiiDataConnectorDataTypes
        friendly_name: Optional[str]
        password: Optional[str]
        polling_frequency: Union[str, PollingFrequency]
        taxii_lookback_period: Optional[datetime]
        taxii_server: Optional[str]
        tenant_id: str
        user_name: Optional[str]
        workspace_id: Optional[str]

        @overload
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
                workspace_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TiType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAIN = "main"


    class azure.mgmt.securityinsight.models.TimelineAggregation(_Model):
        count: int
        kind: Union[str, EntityTimelineKind]

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                kind: Union[str, EntityTimelineKind]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TimelineError(_Model):
        error_message: str
        kind: Union[str, EntityTimelineKind]
        query_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_message: str, 
                kind: Union[str, EntityTimelineKind], 
                query_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TimelineResultsMetadata(_Model):
        aggregations: list[TimelineAggregation]
        errors: Optional[list[TimelineError]]
        total_count: int

        @overload
        def __init__(
                self, 
                *, 
                aggregations: list[TimelineAggregation], 
                errors: Optional[list[TimelineError]] = ..., 
                total_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TriggerOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        LESS_THAN = "LessThan"
        NOT_EQUAL = "NotEqual"


    class azure.mgmt.securityinsight.models.TriggeredAnalyticsRuleRun(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: TriggeredAnalyticsRuleRunProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: TriggeredAnalyticsRuleRunProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.TriggeredAnalyticsRuleRunProperties(_Model):
        execution_time_utc: datetime
        provisioning_state: Union[str, ProvisioningState]
        rule_id: str
        rule_run_additional_data: Optional[dict[str, Any]]
        triggered_analytics_rule_run_id: str

        @overload
        def __init__(
                self, 
                *, 
                execution_time_utc: datetime, 
                rule_id: str, 
                rule_run_additional_data: Optional[dict[str, Any]] = ..., 
                triggered_analytics_rule_run_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.TriggersOn(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"
        INCIDENTS = "Incidents"


    class azure.mgmt.securityinsight.models.TriggersWhen(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        UPDATED = "Updated"


    class azure.mgmt.securityinsight.models.Ueba(Settings, discriminator='Ueba'):
        etag: str
        id: str
        kind: Literal[SettingKind.UEBA]
        name: str
        properties: Optional[UebaProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[UebaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.UebaDataSources(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT_LOGS = "AuditLogs"
        AZURE_ACTIVITY = "AzureActivity"
        SECURITY_EVENT = "SecurityEvent"
        SIGNIN_LOGS = "SigninLogs"


    class azure.mgmt.securityinsight.models.UebaProperties(_Model):
        data_sources: Optional[list[Union[str, UebaDataSources]]]

        @overload
        def __init__(
                self, 
                *, 
                data_sources: Optional[list[Union[str, UebaDataSources]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.UrlEntity(Entity, discriminator='Url'):
        id: str
        kind: Literal[EntityKind.URL]
        name: str
        properties: Optional[UrlEntityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UrlEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.UrlEntityProperties(EntityCommonProperties):
        additional_data: dict[str, any]
        friendly_name: str
        url: Optional[str]


    class azure.mgmt.securityinsight.models.UserInfo(_Model):
        email: Optional[str]
        name: Optional[str]
        object_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.ValidationError(_Model):
        error_messages: Optional[list[str]]
        record_index: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                record_index: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.Version(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V1 = "V1"
        V2 = "V2"


    class azure.mgmt.securityinsight.models.Warning(_Model):
        warning: Optional[WarningBody]


    class azure.mgmt.securityinsight.models.WarningBody(_Model):
        code: Optional[Union[str, WarningCode]]
        details: Optional[list[WarningBody]]
        message: Optional[str]


    class azure.mgmt.securityinsight.models.WarningCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SOURCE_CONTROL_DELETED_WITH_WARNINGS = "SourceControl_DeletedWithWarnings"
        SOURCE_CONTROL_WARNING_DELETE_PIPELINE_FROM_AZURE_DEV_OPS = "SourceControlWarning_DeletePipelineFromAzureDevOps"
        SOURCE_CONTROL_WARNING_DELETE_ROLE_ASSIGNMENT = "SourceControlWarning_DeleteRoleAssignment"
        SOURCE_CONTROL_WARNING_DELETE_SERVICE_PRINCIPAL = "SourceControlWarning_DeleteServicePrincipal"
        SOURCE_CONTROL_WARNING_DELETE_WORKFLOW_AND_SECRET_FROM_GIT_HUB = "SourceControlWarning_DeleteWorkflowAndSecretFromGitHub"


    class azure.mgmt.securityinsight.models.Watchlist(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[WatchlistProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[WatchlistProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.WatchlistItem(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[WatchlistItemProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[WatchlistItemProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.WatchlistItemProperties(_Model):
        created: Optional[datetime]
        created_by: Optional[UserInfo]
        entity_mapping: Optional[Any]
        is_deleted: Optional[bool]
        items_key_value: Any
        tenant_id: Optional[str]
        updated: Optional[datetime]
        updated_by: Optional[UserInfo]
        watchlist_item_id: Optional[str]
        watchlist_item_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                created_by: Optional[UserInfo] = ..., 
                entity_mapping: Optional[Any] = ..., 
                is_deleted: Optional[bool] = ..., 
                items_key_value: Any, 
                tenant_id: Optional[str] = ..., 
                updated: Optional[datetime] = ..., 
                updated_by: Optional[UserInfo] = ..., 
                watchlist_item_id: Optional[str] = ..., 
                watchlist_item_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.WatchlistProperties(_Model):
        content_type: Optional[str]
        created: Optional[datetime]
        created_by: Optional[UserInfo]
        default_duration: Optional[timedelta]
        description: Optional[str]
        display_name: str
        is_deleted: Optional[bool]
        items_search_key: str
        labels: Optional[list[str]]
        number_of_lines_to_skip: Optional[int]
        provider: str
        provisioning_state: Optional[Union[str, WatchlistProvisioningState]]
        raw_content: Optional[str]
        source: Optional[str]
        source_type: Optional[Union[str, SourceType]]
        tenant_id: Optional[str]
        updated: Optional[datetime]
        updated_by: Optional[UserInfo]
        upload_status: Optional[str]
        watchlist_alias: Optional[str]
        watchlist_id: Optional[str]
        watchlist_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_type: Optional[str] = ..., 
                created: Optional[datetime] = ..., 
                created_by: Optional[UserInfo] = ..., 
                default_duration: Optional[timedelta] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                is_deleted: Optional[bool] = ..., 
                items_search_key: str, 
                labels: Optional[list[str]] = ..., 
                number_of_lines_to_skip: Optional[int] = ..., 
                provider: str, 
                raw_content: Optional[str] = ..., 
                source: Optional[str] = ..., 
                source_type: Optional[Union[str, SourceType]] = ..., 
                tenant_id: Optional[str] = ..., 
                updated: Optional[datetime] = ..., 
                updated_by: Optional[UserInfo] = ..., 
                upload_status: Optional[str] = ..., 
                watchlist_alias: Optional[str] = ..., 
                watchlist_id: Optional[str] = ..., 
                watchlist_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.WatchlistProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NEW = "New"
        SUCCEEDED = "Succeeded"
        UPLOADING = "Uploading"


    class azure.mgmt.securityinsight.models.Webhook(_Model):
        rotate_webhook_secret: Optional[bool]
        webhook_id: Optional[str]
        webhook_secret_update_time: Optional[datetime]
        webhook_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                rotate_webhook_secret: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.WorkloadIdentityFederation(_Model):
        app_id: Optional[str]
        id: Optional[str]
        issuer: Optional[str]
        subject: Optional[str]
        tenant_id: Optional[str]


    class azure.mgmt.securityinsight.models.WorkspaceManagerAssignment(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[WorkspaceManagerAssignmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkspaceManagerAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.WorkspaceManagerAssignmentProperties(_Model):
        items_property: list[AssignmentItem]
        last_job_end_time: Optional[datetime]
        last_job_provisioning_state: Optional[Union[str, JobProvisioningState]]
        target_resource_name: str

        @overload
        def __init__(
                self, 
                *, 
                items_property: list[AssignmentItem], 
                target_resource_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.WorkspaceManagerConfiguration(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[WorkspaceManagerConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkspaceManagerConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.WorkspaceManagerConfigurationProperties(_Model):
        mode: Union[str, Mode]

        @overload
        def __init__(
                self, 
                *, 
                mode: Union[str, Mode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.WorkspaceManagerGroup(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[WorkspaceManagerGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkspaceManagerGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.WorkspaceManagerGroupProperties(_Model):
        description: Optional[str]
        display_name: str
        member_resource_names: list[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: str, 
                member_resource_names: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.securityinsight.models.WorkspaceManagerMember(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[WorkspaceManagerMemberProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkspaceManagerMemberProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.models.WorkspaceManagerMemberProperties(_Model):
        target_workspace_resource_id: str
        target_workspace_tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                target_workspace_resource_id: str, 
                target_workspace_tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.securityinsight.operations

    class azure.mgmt.securityinsight.operations.ActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                action: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                action_id: str, 
                **kwargs: Any
            ) -> ActionResponse: ...

        @distributed_trace
        def list_by_alert_rule(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                **kwargs: Any
            ) -> ItemPaged[ActionResponse]: ...


    class azure.mgmt.securityinsight.operations.AlertRuleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_trigger_rule_run(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                analytics_rule_run_trigger_parameter: AnalyticsRuleRunTrigger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_rule_run(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                analytics_rule_run_trigger_parameter: AnalyticsRuleRunTrigger, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_trigger_rule_run(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                analytics_rule_run_trigger_parameter: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.securityinsight.operations.AlertRuleTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                alert_rule_template_id: str, 
                **kwargs: Any
            ) -> AlertRuleTemplate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AlertRuleTemplate]: ...


    class azure.mgmt.securityinsight.operations.AlertRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                alert_rule: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_id: str, 
                **kwargs: Any
            ) -> AlertRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AlertRule]: ...


    class azure.mgmt.securityinsight.operations.AutomationRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                automation_rule_to_upsert: Optional[IO[bytes]] = None, 
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
                **kwargs: Any
            ) -> Any: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                automation_rule_id: str, 
                **kwargs: Any
            ) -> AutomationRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AutomationRule]: ...


    class azure.mgmt.securityinsight.operations.BillingStatisticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'billing_statistic_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                billing_statistic_name: str, 
                **kwargs: Any
            ) -> BillingStatistic: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BillingStatistic]: ...


    class azure.mgmt.securityinsight.operations.BookmarkOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BookmarkExpandResponse: ...


    class azure.mgmt.securityinsight.operations.BookmarkRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                relation: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'bookmark_id', 'relation_name']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'bookmark_id', 'relation_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                relation_name: str, 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'bookmark_id', 'filter', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Relation]: ...


    class azure.mgmt.securityinsight.operations.BookmarksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                bookmark: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                bookmark_id: str, 
                **kwargs: Any
            ) -> Bookmark: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Bookmark]: ...


    class azure.mgmt.securityinsight.operations.ContentPackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                package_id: str, 
                package_installation_properties: PackageModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PackageModel: ...

        @overload
        def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                package_id: str, 
                package_installation_properties: PackageModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PackageModel: ...

        @overload
        def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                package_id: str, 
                package_installation_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PackageModel: ...

        @distributed_trace
        def uninstall(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                package_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.operations.ContentPackagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                package_id: str, 
                **kwargs: Any
            ) -> PackageModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PackageModel]: ...


    class azure.mgmt.securityinsight.operations.ContentTemplateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                template_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                template_id: str, 
                **kwargs: Any
            ) -> TemplateModel: ...

        @overload
        def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                template_id: str, 
                template_installation_properties: TemplateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateModel: ...

        @overload
        def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                template_id: str, 
                template_installation_properties: TemplateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateModel: ...

        @overload
        def install(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                template_id: str, 
                template_installation_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateModel: ...


    class azure.mgmt.securityinsight.operations.ContentTemplatesOperations:

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
                *, 
                count: Optional[bool] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TemplateModel]: ...


    class azure.mgmt.securityinsight.operations.DataConnectorDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_definition_name: str, 
                connector_definition_input: DataConnectorDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorDefinition: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_definition_name: str, 
                connector_definition_input: DataConnectorDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorDefinition: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_definition_name: str, 
                connector_definition_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorDefinition: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_definition_name: str, 
                **kwargs: Any
            ) -> DataConnectorDefinition: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataConnectorDefinition]: ...


    class azure.mgmt.securityinsight.operations.DataConnectorsCheckRequirementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                data_connectors_check_requirements: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataConnectorRequirementsState: ...


    class azure.mgmt.securityinsight.operations.DataConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                connect_body: IO[bytes], 
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
                data_connector: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'data_connector_id']}, api_versions_list=['2025-10-01-preview'])
        def disconnect(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                data_connector_id: str, 
                **kwargs: Any
            ) -> DataConnector: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataConnector]: ...


    class azure.mgmt.securityinsight.operations.EntitiesGetTimelineOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityTimelineResponse: ...


    class azure.mgmt.securityinsight.operations.EntitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityExpandResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityGetInsightsResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Entity]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_id', 'kind', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def queries(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                *, 
                kind: Union[str, EntityItemQueryKind], 
                **kwargs: Any
            ) -> ItemPaged[EntityQueryItem]: ...

        @overload
        def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_identifier: str, 
                request_body: Optional[EntityManualTriggerRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_identifier: str, 
                request_body: Optional[EntityManualTriggerRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_identifier: str, 
                request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.securityinsight.operations.EntitiesRelationsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Relation]: ...


    class azure.mgmt.securityinsight.operations.EntityQueriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                entity_query: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityQuery: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_query_id']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_query_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_id: str, 
                **kwargs: Any
            ) -> EntityQuery: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'kind', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                kind: Optional[Union[str, EntityQueryTemplateKind]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EntityQuery]: ...


    class azure.mgmt.securityinsight.operations.EntityQueryTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_query_template_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_query_template_id: str, 
                **kwargs: Any
            ) -> EntityQueryTemplate: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'kind', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                kind: Optional[Union[str, EntityQueryTemplateKind]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EntityQueryTemplate]: ...


    class azure.mgmt.securityinsight.operations.EntityRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'entity_id', 'relation_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get_relation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                entity_id: str, 
                relation_name: str, 
                **kwargs: Any
            ) -> Relation: ...


    class azure.mgmt.securityinsight.operations.FileImportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'file_import_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
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
                file_import: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileImport: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'file_import_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                file_import_id: str, 
                **kwargs: Any
            ) -> FileImport: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'filter', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[FileImport]: ...


    class azure.mgmt.securityinsight.operations.GetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def single_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                **kwargs: Any
            ) -> Recommendation: ...


    class azure.mgmt.securityinsight.operations.GetRecommendationsOperations:

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
                **kwargs: Any
            ) -> ItemPaged[Recommendation]: ...


    class azure.mgmt.securityinsight.operations.GetTriggeredAnalyticsRuleRunsOperations:

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
                **kwargs: Any
            ) -> ItemPaged[TriggeredAnalyticsRuleRun]: ...


    class azure.mgmt.securityinsight.operations.HuntCommentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_comment_id: str, 
                hunt_comment: HuntComment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntComment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_comment_id: str, 
                hunt_comment: HuntComment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntComment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_comment_id: str, 
                hunt_comment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntComment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'hunt_comment_id']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_comment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'hunt_comment_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_comment_id: str, 
                **kwargs: Any
            ) -> HuntComment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'filter', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[HuntComment]: ...


    class azure.mgmt.securityinsight.operations.HuntRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_relation_id: str, 
                hunt_relation: HuntRelation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntRelation: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_relation_id: str, 
                hunt_relation: HuntRelation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntRelation: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_relation_id: str, 
                hunt_relation: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HuntRelation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'hunt_relation_id']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_relation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'hunt_relation_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt_relation_id: str, 
                **kwargs: Any
            ) -> HuntRelation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'filter', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[HuntRelation]: ...


    class azure.mgmt.securityinsight.operations.HuntsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt: Hunt, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Hunt: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt: Hunt, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Hunt: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                hunt: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Hunt: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'hunt_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                hunt_id: str, 
                **kwargs: Any
            ) -> Hunt: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'filter', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Hunt]: ...


    class azure.mgmt.securityinsight.operations.IncidentCommentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                incident_comment: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_comment_id: str, 
                **kwargs: Any
            ) -> IncidentComment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[IncidentComment]: ...


    class azure.mgmt.securityinsight.operations.IncidentRelationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                relation: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                relation_name: str, 
                **kwargs: Any
            ) -> Relation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Relation]: ...


    class azure.mgmt.securityinsight.operations.IncidentTasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                incident_task: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                incident_task_id: str, 
                **kwargs: Any
            ) -> IncidentTask: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                **kwargs: Any
            ) -> ItemPaged[IncidentTask]: ...


    class azure.mgmt.securityinsight.operations.IncidentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                incident: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Incident: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                **kwargs: Any
            ) -> Incident: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Incident]: ...

        @distributed_trace
        def list_alerts(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                **kwargs: Any
            ) -> IncidentAlertList: ...

        @distributed_trace
        def list_bookmarks(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
                **kwargs: Any
            ) -> IncidentBookmarkList: ...

        @distributed_trace
        def list_entities(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_id: str, 
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
            ) -> Any: ...

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
            ) -> Any: ...

        @overload
        def run_playbook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                incident_identifier: str, 
                request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...


    class azure.mgmt.securityinsight.operations.MetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                metadata: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                metadata_name: str, 
                **kwargs: Any
            ) -> MetadataModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MetadataModel]: ...

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
                metadata_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataModel: ...


    class azure.mgmt.securityinsight.operations.OfficeConsentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'consent_id']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                consent_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'consent_id', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                consent_id: str, 
                **kwargs: Any
            ) -> OfficeConsent: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OfficeConsent]: ...


    class azure.mgmt.securityinsight.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.securityinsight.operations.ProductPackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                package_id: str, 
                **kwargs: Any
            ) -> ProductPackageModel: ...


    class azure.mgmt.securityinsight.operations.ProductPackagesOperations:

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
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProductPackageModel]: ...


    class azure.mgmt.securityinsight.operations.ProductSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'settings_name']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'settings_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_name: str, 
                **kwargs: Any
            ) -> Settings: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Settings]: ...

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
                settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Settings: ...


    class azure.mgmt.securityinsight.operations.ProductTemplateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                template_id: str, 
                **kwargs: Any
            ) -> ProductTemplateModel: ...


    class azure.mgmt.securityinsight.operations.ProductTemplatesOperations:

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
                *, 
                count: Optional[bool] = ..., 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProductTemplateModel]: ...


    class azure.mgmt.securityinsight.operations.ReevaluateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                **kwargs: Any
            ) -> ReevaluateResponse: ...


    class azure.mgmt.securityinsight.operations.SecurityMLAnalyticsSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                security_ml_analytics_setting: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                settings_resource_name: str, 
                **kwargs: Any
            ) -> SecurityMLAnalyticsSetting: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SecurityMLAnalyticsSetting]: ...


    class azure.mgmt.securityinsight.operations.SentinelOnboardingStatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                sentinel_onboarding_state_parameter: Optional[IO[bytes]] = None, 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sentinel_onboarding_state_name: str, 
                **kwargs: Any
            ) -> SentinelOnboardingState: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> SentinelOnboardingStatesList: ...


    class azure.mgmt.securityinsight.operations.SourceControlOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list_repositories(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                repository_access: RepositoryAccessProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[Repo]: ...

        @overload
        def list_repositories(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                repository_access: RepositoryAccessProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[Repo]: ...

        @overload
        def list_repositories(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                repository_access: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[Repo]: ...


    class azure.mgmt.securityinsight.operations.SourceControlsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                source_control: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @overload
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                repository_access: RepositoryAccessProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Warning: ...

        @overload
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                repository_access: RepositoryAccessProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Warning: ...

        @overload
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                repository_access: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Warning: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                source_control_id: str, 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SourceControl]: ...


    class azure.mgmt.securityinsight.operations.ThreatIntelligenceIndicatorMetricsOperations:

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
                **kwargs: Any
            ) -> ThreatIntelligenceMetricsList: ...


    class azure.mgmt.securityinsight.operations.ThreatIntelligenceIndicatorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                threat_intelligence_append_tags: IO[bytes], 
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
                threat_intelligence_properties: IO[bytes], 
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
                threat_intelligence_properties: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
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
            ) -> ItemPaged[ThreatIntelligenceInformation]: ...

        @overload
        def query_indicators(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_filtering_criteria: ThreatIntelligenceFilteringCriteria, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[ThreatIntelligenceInformation]: ...

        @overload
        def query_indicators(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                threat_intelligence_filtering_criteria: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[ThreatIntelligenceInformation]: ...

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
                threat_intelligence_replace_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceInformation: ...


    class azure.mgmt.securityinsight.operations.ThreatIntelligenceIndicatorsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ThreatIntelligenceInformation]: ...


    class azure.mgmt.securityinsight.operations.ThreatIntelligenceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def count(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[CountQuery] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceCount: ...

        @overload
        def count(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[CountQuery] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceCount: ...

        @overload
        def count(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreatIntelligenceCount: ...

        @overload
        def query(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[Query] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[TIObject]: ...

        @overload
        def query(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[Query] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[TIObject]: ...

        @overload
        def query(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                ti_type: Union[str, TiType], 
                query: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[TIObject]: ...


    class azure.mgmt.securityinsight.operations.TriggeredAnalyticsRuleRunOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_run_id: str, 
                **kwargs: Any
            ) -> TriggeredAnalyticsRuleRun: ...


    class azure.mgmt.securityinsight.operations.UpdateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                recommendation_patch: RecommendationPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Recommendation: ...

        @overload
        def recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                recommendation_patch: RecommendationPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Recommendation: ...

        @overload
        def recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                recommendation_id: str, 
                recommendation_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Recommendation: ...


    class azure.mgmt.securityinsight.operations.WatchlistItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                watchlist_item: IO[bytes], 
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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist_item_id: str, 
                **kwargs: Any
            ) -> WatchlistItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[WatchlistItem]: ...


    class azure.mgmt.securityinsight.operations.WatchlistsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist: Watchlist, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Watchlist]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist: Watchlist, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Watchlist]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                watchlist: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Watchlist]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                **kwargs: Any
            ) -> LROPoller[Watchlist]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                watchlist_alias: str, 
                **kwargs: Any
            ) -> Watchlist: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Watchlist]: ...


    class azure.mgmt.securityinsight.operations.WorkspaceManagerAssignmentJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                *, 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Job]: ...


    class azure.mgmt.securityinsight.operations.WorkspaceManagerAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                workspace_manager_assignment: WorkspaceManagerAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerAssignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                workspace_manager_assignment: WorkspaceManagerAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerAssignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                workspace_manager_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerAssignment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_assignment_name']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_assignment_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_assignment_name: str, 
                **kwargs: Any
            ) -> WorkspaceManagerAssignment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[WorkspaceManagerAssignment]: ...


    class azure.mgmt.securityinsight.operations.WorkspaceManagerConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_configuration_name: str, 
                workspace_manager_configuration: WorkspaceManagerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_configuration_name: str, 
                workspace_manager_configuration: WorkspaceManagerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_configuration_name: str, 
                workspace_manager_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_configuration_name']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_configuration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_configuration_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_configuration_name: str, 
                **kwargs: Any
            ) -> WorkspaceManagerConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[WorkspaceManagerConfiguration]: ...


    class azure.mgmt.securityinsight.operations.WorkspaceManagerGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_group_name: str, 
                workspace_manager_group: WorkspaceManagerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_group_name: str, 
                workspace_manager_group: WorkspaceManagerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_group_name: str, 
                workspace_manager_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerGroup: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_group_name']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_group_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_group_name: str, 
                **kwargs: Any
            ) -> WorkspaceManagerGroup: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[WorkspaceManagerGroup]: ...


    class azure.mgmt.securityinsight.operations.WorkspaceManagerMembersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_member_name: str, 
                workspace_manager_member: WorkspaceManagerMember, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerMember: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_member_name: str, 
                workspace_manager_member: WorkspaceManagerMember, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerMember: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_member_name: str, 
                workspace_manager_member: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceManagerMember: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_member_name']}, api_versions_list=['2025-10-01-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_member_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'workspace_manager_member_name', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_manager_member_name: str, 
                **kwargs: Any
            ) -> WorkspaceManagerMember: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01-preview', params_added_on={'2025-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'orderby', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-10-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                orderby: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[WorkspaceManagerMember]: ...


namespace azure.mgmt.securityinsight.types

    class azure.mgmt.securityinsight.types.AADCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.AZURE_ACTIVE_DIRECTORY]]
        key "properties": ForwardRef('AADCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.AZURE_ACTIVE_DIRECTORY]
        properties: AADCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.AADCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.AADDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.AZURE_ACTIVE_DIRECTORY]]
        key "name": str
        key "properties": ForwardRef('AADDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.AZURE_ACTIVE_DIRECTORY]
        name: str
        properties: AADDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.AADDataConnectorProperties(TypedDict, total=False):
        key "dataTypes": ForwardRef('AlertsDataTypeOfDataConnector', module='types')
        key "tenantId": Required[str]
        dataTypes: AlertsDataTypeOfDataConnector
        tenantId: str


    class azure.mgmt.securityinsight.types.AATPCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.AZURE_ADVANCED_THREAT_PROTECTION]]
        key "properties": ForwardRef('AATPCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.AZURE_ADVANCED_THREAT_PROTECTION]
        properties: AATPCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.AATPCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.AATPDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.AZURE_ADVANCED_THREAT_PROTECTION]]
        key "name": str
        key "properties": ForwardRef('AATPDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.AZURE_ADVANCED_THREAT_PROTECTION]
        name: str
        properties: AATPDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.AATPDataConnectorProperties(TypedDict, total=False):
        key "dataTypes": ForwardRef('AlertsDataTypeOfDataConnector', module='types')
        key "tenantId": Required[str]
        dataTypes: AlertsDataTypeOfDataConnector
        tenantId: str


    class azure.mgmt.securityinsight.types.ASCCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.AZURE_SECURITY_CENTER]]
        key "properties": ForwardRef('ASCCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.AZURE_SECURITY_CENTER]
        properties: ASCCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.ASCCheckRequirementsProperties(TypedDict, total=False):
        key "subscriptionId": str
        subscriptionId: str


    class azure.mgmt.securityinsight.types.ASCDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.AZURE_SECURITY_CENTER]]
        key "name": str
        key "properties": ForwardRef('ASCDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.AZURE_SECURITY_CENTER]
        name: str
        properties: ASCDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.ASCDataConnectorProperties(DataConnectorWithAlertsProperties):
        key "dataTypes": ForwardRef('AlertsDataTypeOfDataConnector', module='types')
        key "subscriptionId": str
        dataTypes: AlertsDataTypeOfDataConnector
        subscriptionId: str


    class azure.mgmt.securityinsight.types.AWSAuthModel(TypedDict, total=False):
        key "externalId": str
        key "roleArn": Required[str]
        key "type": Required[Literal[CcpAuthType.AWS]]
        externalId: str
        roleArn: str
        type: Literal[CcpAuthType.AWS]


    class azure.mgmt.securityinsight.types.ActionPropertiesBase(TypedDict, total=False):
        key "logicAppResourceId": Required[str]
        logicAppResourceId: str


    class azure.mgmt.securityinsight.types.ActionRequest(ResourceWithEtag):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ActionRequestProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: ActionRequestProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.ActionRequestProperties(ActionPropertiesBase):
        key "logicAppResourceId": Required[str]
        key "triggerUri": Required[str]
        logicAppResourceId: str
        triggerUri: str


    class azure.mgmt.securityinsight.types.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_INCIDENT_TASK = "AddIncidentTask"
        MODIFY_PROPERTIES = "ModifyProperties"
        RUN_PLAYBOOK = "RunPlaybook"


    class azure.mgmt.securityinsight.types.ActivityCustomEntityQuery(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[CustomEntityQueryKind.ACTIVITY]]
        key "name": str
        key "properties": ForwardRef('ActivityEntityQueriesProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[CustomEntityQueryKind.ACTIVITY]
        name: str
        properties: ActivityEntityQueriesProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.ActivityEntityQueriesProperties(TypedDict, total=False):
        key "content": str
        key "createdTimeUtc": str
        key "description": str
        key "enabled": bool
        key "inputEntityType": Union[str, EntityType]
        key "lastModifiedTimeUtc": str
        key "queryDefinitions": ForwardRef('ActivityEntityQueriesPropertiesQueryDefinitions', module='types')
        key "templateName": str
        key "title": str
        content: str
        createdTimeUtc: str
        description: str
        enabled: bool
        entitiesFilter: dict[str, list[str]]
        inputEntityType: Union[str, EntityType]
        lastModifiedTimeUtc: str
        queryDefinitions: ActivityEntityQueriesPropertiesQueryDefinitions
        requiredInputFieldsSets: list[list[str]]
        templateName: str
        title: str


    class azure.mgmt.securityinsight.types.ActivityEntityQueriesPropertiesQueryDefinitions(TypedDict, total=False):
        key "query": str
        query: str


    class azure.mgmt.securityinsight.types.AddIncidentTaskActionProperties(TypedDict, total=False):
        key "description": str
        key "title": Required[str]
        description: str
        title: str


    class azure.mgmt.securityinsight.types.AlertDetailsOverride(TypedDict, total=False):
        key "alertDescriptionFormat": str
        key "alertDisplayNameFormat": str
        key "alertSeverityColumnName": str
        key "alertTacticsColumnName": str
        alertDescriptionFormat: str
        alertDisplayNameFormat: str
        alertDynamicProperties: list[AlertPropertyMapping]
        alertSeverityColumnName: str
        alertTacticsColumnName: str


    class azure.mgmt.securityinsight.types.AlertPropertyMapping(TypedDict, total=False):
        key "alertProperty": Union[str, AlertProperty]
        key "value": str
        alertProperty: Union[str, AlertProperty]
        value: str


    class azure.mgmt.securityinsight.types.AlertRuleKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUSION = "Fusion"
        MICROSOFT_SECURITY_INCIDENT_CREATION = "MicrosoftSecurityIncidentCreation"
        ML_BEHAVIOR_ANALYTICS = "MLBehaviorAnalytics"
        NRT = "NRT"
        SCHEDULED = "Scheduled"
        THREAT_INTELLIGENCE = "ThreatIntelligence"


    class azure.mgmt.securityinsight.types.AlertsDataTypeOfDataConnector(TypedDict, total=False):
        key "alerts": Required[DataConnectorDataTypeCommon]
        alerts: DataConnectorDataTypeCommon


    class azure.mgmt.securityinsight.types.AnalyticsRuleRunTrigger(TypedDict, total=False):
        key "properties": Required[AnalyticsRuleRunTriggerProperties]
        properties: AnalyticsRuleRunTriggerProperties


    class azure.mgmt.securityinsight.types.AnalyticsRuleRunTriggerProperties(TypedDict, total=False):
        key "executionTimeUtc": Required[str]
        executionTimeUtc: str


    class azure.mgmt.securityinsight.types.Anomalies(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[SettingKind.ANOMALIES]]
        key "name": str
        key "properties": ForwardRef('AnomaliesSettingsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[SettingKind.ANOMALIES]
        name: str
        properties: AnomaliesSettingsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.AnomaliesSettingsProperties(TypedDict, total=False):
        key "isEnabled": bool
        isEnabled: bool


    class azure.mgmt.securityinsight.types.AnomalySecurityMLAnalyticsSettings(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[SecurityMLAnalyticsSettingsKind.ANOMALY]]
        key "name": str
        key "properties": ForwardRef('AnomalySecurityMLAnalyticsSettingsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[SecurityMLAnalyticsSettingsKind.ANOMALY]
        name: str
        properties: AnomalySecurityMLAnalyticsSettingsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.AnomalySecurityMLAnalyticsSettingsProperties(TypedDict, total=False):
        key "anomalySettingsVersion": int
        key "anomalyVersion": Required[str]
        key "customizableObservations": Any
        key "description": str
        key "displayName": Required[str]
        key "enabled": Required[bool]
        key "frequency": Required[str]
        key "isDefaultSettings": Required[bool]
        key "lastModifiedUtc": str
        key "settingsDefinitionId": str
        key "settingsStatus": Required[Union[str, SettingsStatus]]
        anomalySettingsVersion: int
        anomalyVersion: str
        customizableObservations: Any
        description: str
        displayName: str
        enabled: bool
        frequency: str
        isDefaultSettings: bool
        lastModifiedUtc: str
        requiredDataConnectors: list[SecurityMLAnalyticsSettingsDataSource]
        settingsDefinitionId: str
        settingsStatus: Union[str, SettingsStatus]
        tactics: list[Union[str, AttackTactic]]
        techniques: list[str]


    class azure.mgmt.securityinsight.types.ApiKeyAuthModel(TypedDict, total=False):
        key "apiKey": Required[str]
        key "apiKeyIdentifier": str
        key "apiKeyName": Required[str]
        key "isApiKeyInPostPayload": bool
        key "type": Required[Literal[CcpAuthType.API_KEY]]
        apiKey: str
        apiKeyIdentifier: str
        apiKeyName: str
        isApiKeyInPostPayload: bool
        type: Literal[CcpAuthType.API_KEY]


    class azure.mgmt.securityinsight.types.ApiPollingParameters(TypedDict, total=False):
        key "connectorUiConfig": ForwardRef('CodelessUiConnectorConfigProperties', module='types')
        key "pollingConfig": ForwardRef('CodelessConnectorPollingConfigProperties', module='types')
        connectorUiConfig: CodelessUiConnectorConfigProperties
        pollingConfig: CodelessConnectorPollingConfigProperties


    class azure.mgmt.securityinsight.types.AssignmentItem(TypedDict, total=False):
        key "resourceId": str
        resourceId: str


    class azure.mgmt.securityinsight.types.AutomationRule(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": Required[AutomationRuleProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: AutomationRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.AutomationRuleAddIncidentTaskAction(TypedDict, total=False):
        key "actionConfiguration": ForwardRef('AddIncidentTaskActionProperties', module='types')
        key "actionType": Required[Literal[ActionType.ADD_INCIDENT_TASK]]
        key "order": Required[int]
        actionConfiguration: AddIncidentTaskActionProperties
        actionType: Literal[ActionType.ADD_INCIDENT_TASK]
        order: int


    class azure.mgmt.securityinsight.types.AutomationRuleBooleanCondition(TypedDict, total=False):
        key "operator": Union[str, AutomationRuleBooleanConditionSupportedOperator]
        innerConditions: list[AutomationRuleCondition]
        operator: Union[str, AutomationRuleBooleanConditionSupportedOperator]


    class azure.mgmt.securityinsight.types.AutomationRuleModifyPropertiesAction(TypedDict, total=False):
        key "actionConfiguration": ForwardRef('IncidentPropertiesAction', module='types')
        key "actionType": Required[Literal[ActionType.MODIFY_PROPERTIES]]
        key "order": Required[int]
        actionConfiguration: IncidentPropertiesAction
        actionType: Literal[ActionType.MODIFY_PROPERTIES]
        order: int


    class azure.mgmt.securityinsight.types.AutomationRuleProperties(TypedDict, total=False):
        key "actions": Required[list[AutomationRuleAction]]
        key "createdBy": ForwardRef('ClientInfo', module='types')
        key "createdTimeUtc": str
        key "displayName": Required[str]
        key "lastModifiedBy": ForwardRef('ClientInfo', module='types')
        key "lastModifiedTimeUtc": str
        key "order": Required[int]
        key "triggeringLogic": Required[AutomationRuleTriggeringLogic]
        actions: list[AutomationRuleAction]
        createdBy: ClientInfo
        createdTimeUtc: str
        displayName: str
        lastModifiedBy: ClientInfo
        lastModifiedTimeUtc: str
        order: int
        triggeringLogic: AutomationRuleTriggeringLogic


    class azure.mgmt.securityinsight.types.AutomationRulePropertyArrayChangedValuesCondition(TypedDict, total=False):
        key "arrayType": Union[str, AutomationRulePropertyArrayChangedConditionSupportedArrayType]
        key "changeType": Union[str, AutomationRulePropertyArrayChangedConditionSupportedChangeType]
        arrayType: Union[str, AutomationRulePropertyArrayChangedConditionSupportedArrayType]
        changeType: Union[str, AutomationRulePropertyArrayChangedConditionSupportedChangeType]


    class azure.mgmt.securityinsight.types.AutomationRulePropertyArrayValuesCondition(TypedDict, total=False):
        key "arrayConditionType": Union[str, AutomationRulePropertyArrayConditionSupportedArrayConditionType]
        key "arrayType": Union[str, AutomationRulePropertyArrayConditionSupportedArrayType]
        arrayConditionType: Union[str, AutomationRulePropertyArrayConditionSupportedArrayConditionType]
        arrayType: Union[str, AutomationRulePropertyArrayConditionSupportedArrayType]
        itemConditions: list[AutomationRuleCondition]


    class azure.mgmt.securityinsight.types.AutomationRulePropertyValuesChangedCondition(TypedDict, total=False):
        key "changeType": Union[str, AutomationRulePropertyChangedConditionSupportedChangedType]
        key "operator": Union[str, AutomationRulePropertyConditionSupportedOperator]
        key "propertyName": Union[str, AutomationRulePropertyChangedConditionSupportedPropertyType]
        changeType: Union[str, AutomationRulePropertyChangedConditionSupportedChangedType]
        operator: Union[str, AutomationRulePropertyConditionSupportedOperator]
        propertyName: Union[str, AutomationRulePropertyChangedConditionSupportedPropertyType]
        propertyValues: list[str]


    class azure.mgmt.securityinsight.types.AutomationRulePropertyValuesCondition(TypedDict, total=False):
        key "operator": Union[str, AutomationRulePropertyConditionSupportedOperator]
        key "propertyName": Union[str, AutomationRulePropertyConditionSupportedProperty]
        operator: Union[str, AutomationRulePropertyConditionSupportedOperator]
        propertyName: Union[str, AutomationRulePropertyConditionSupportedProperty]
        propertyValues: list[str]


    class azure.mgmt.securityinsight.types.AutomationRuleRunPlaybookAction(TypedDict, total=False):
        key "actionConfiguration": ForwardRef('PlaybookActionProperties', module='types')
        key "actionType": Required[Literal[ActionType.RUN_PLAYBOOK]]
        key "order": Required[int]
        actionConfiguration: PlaybookActionProperties
        actionType: Literal[ActionType.RUN_PLAYBOOK]
        order: int


    class azure.mgmt.securityinsight.types.AutomationRuleTriggeringLogic(TypedDict, total=False):
        key "expirationTimeUtc": str
        key "isEnabled": Required[bool]
        key "triggersOn": Required[Union[str, TriggersOn]]
        key "triggersWhen": Required[Union[str, TriggersWhen]]
        conditions: list[AutomationRuleCondition]
        expirationTimeUtc: str
        isEnabled: bool
        triggersOn: Union[str, TriggersOn]
        triggersWhen: Union[str, TriggersWhen]


    class azure.mgmt.securityinsight.types.Availability(TypedDict, total=False):
        key "isPreview": bool
        key "status": Literal[1]
        isPreview: bool
        status: Literal[1]


    class azure.mgmt.securityinsight.types.AwsCloudTrailCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.AMAZON_WEB_SERVICES_CLOUD_TRAIL]]
        kind: Literal[DataConnectorKind.AMAZON_WEB_SERVICES_CLOUD_TRAIL]


    class azure.mgmt.securityinsight.types.AwsCloudTrailDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.AMAZON_WEB_SERVICES_CLOUD_TRAIL]]
        key "name": str
        key "properties": ForwardRef('AwsCloudTrailDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.AMAZON_WEB_SERVICES_CLOUD_TRAIL]
        name: str
        properties: AwsCloudTrailDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.AwsCloudTrailDataConnectorDataTypes(TypedDict, total=False):
        key "logs": Required[AwsCloudTrailDataConnectorDataTypesLogs]
        logs: AwsCloudTrailDataConnectorDataTypesLogs


    class azure.mgmt.securityinsight.types.AwsCloudTrailDataConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.AwsCloudTrailDataConnectorProperties(TypedDict, total=False):
        key "awsRoleArn": str
        key "dataTypes": Required[AwsCloudTrailDataConnectorDataTypes]
        awsRoleArn: str
        dataTypes: AwsCloudTrailDataConnectorDataTypes


    class azure.mgmt.securityinsight.types.AwsS3CheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.AMAZON_WEB_SERVICES_S3]]
        kind: Literal[DataConnectorKind.AMAZON_WEB_SERVICES_S3]


    class azure.mgmt.securityinsight.types.AwsS3DataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.AMAZON_WEB_SERVICES_S3]]
        key "name": str
        key "properties": ForwardRef('AwsS3DataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.AMAZON_WEB_SERVICES_S3]
        name: str
        properties: AwsS3DataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.AwsS3DataConnectorDataTypes(TypedDict, total=False):
        key "logs": Required[AwsS3DataConnectorDataTypesLogs]
        logs: AwsS3DataConnectorDataTypesLogs


    class azure.mgmt.securityinsight.types.AwsS3DataConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.AwsS3DataConnectorProperties(TypedDict, total=False):
        key "dataTypes": Required[AwsS3DataConnectorDataTypes]
        key "destinationTable": Required[str]
        key "roleArn": Required[str]
        key "sqsUrls": Required[list[str]]
        dataTypes: AwsS3DataConnectorDataTypes
        destinationTable: str
        roleArn: str
        sqsUrls: list[str]


    class azure.mgmt.securityinsight.types.AzureDevOpsResourceInfo(TypedDict, total=False):
        key "pipelineId": str
        key "serviceConnectionId": str
        pipelineId: str
        serviceConnectionId: str


    class azure.mgmt.securityinsight.types.BasicAuthModel(TypedDict, total=False):
        key "password": Required[str]
        key "type": Required[Literal[CcpAuthType.BASIC]]
        key "userName": Required[str]
        password: str
        type: Literal[CcpAuthType.BASIC]
        userName: str


    class azure.mgmt.securityinsight.types.Bookmark(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('BookmarkProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: BookmarkProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.BookmarkEntityMappings(TypedDict, total=False):
        key "entityType": str
        entityType: str
        fieldMappings: list[EntityFieldMapping]


    class azure.mgmt.securityinsight.types.BookmarkExpandParameters(TypedDict, total=False):
        key "endTime": str
        key "expansionId": str
        key "startTime": str
        endTime: str
        expansionId: str
        startTime: str


    class azure.mgmt.securityinsight.types.BookmarkProperties(TypedDict, total=False):
        key "created": str
        key "createdBy": ForwardRef('UserInfo', module='types')
        key "displayName": Required[str]
        key "eventTime": str
        key "incidentInfo": ForwardRef('IncidentInfo', module='types')
        key "notes": str
        key "query": Required[str]
        key "queryEndTime": str
        key "queryResult": str
        key "queryStartTime": str
        key "updated": str
        key "updatedBy": ForwardRef('UserInfo', module='types')
        created: str
        createdBy: UserInfo
        displayName: str
        entityMappings: list[BookmarkEntityMappings]
        eventTime: str
        incidentInfo: IncidentInfo
        labels: list[str]
        notes: str
        query: str
        queryEndTime: str
        queryResult: str
        queryStartTime: str
        tactics: list[Union[str, AttackTactic]]
        techniques: list[str]
        updated: str
        updatedBy: UserInfo


    class azure.mgmt.securityinsight.types.BooleanConditionProperties(TypedDict, total=False):
        key "conditionProperties": ForwardRef('AutomationRuleBooleanCondition', module='types')
        key "conditionType": Required[Literal[ConditionType.BOOLEAN]]
        conditionProperties: AutomationRuleBooleanCondition
        conditionType: Literal[ConditionType.BOOLEAN]


    class azure.mgmt.securityinsight.types.CcpAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        API_KEY = "APIKey"
        AWS = "AWS"
        BASIC = "Basic"
        GCP = "GCP"
        GIT_HUB = "GitHub"
        JWT_TOKEN = "JwtToken"
        NONE = "None"
        ORACLE = "Oracle"
        O_AUTH2 = "OAuth2"
        SERVICE_BUS = "ServiceBus"
        SESSION = "Session"


    class azure.mgmt.securityinsight.types.CcpResponseConfig(TypedDict, total=False):
        key "compressionAlgo": str
        key "convertChildPropertiesToArray": Optional[bool]
        key "csvDelimiter": str
        key "csvEscape": Optional[str]
        key "eventsJsonPaths": Required[list[str]]
        key "format": str
        key "hasCsvBoundary": Optional[bool]
        key "hasCsvHeader": Optional[bool]
        key "isGzipCompressed": bool
        key "successStatusJsonPath": str
        key "successStatusValue": Optional[str]
        compressionAlgo: str
        convertChildPropertiesToArray: bool
        csvDelimiter: str
        csvEscape: str
        eventsJsonPaths: list[str]
        format: str
        hasCsvBoundary: bool
        hasCsvHeader: bool
        isGzipCompressed: bool
        successStatusJsonPath: str
        successStatusValue: str


    class azure.mgmt.securityinsight.types.ClientInfo(TypedDict, total=False):
        key "email": str
        key "name": str
        key "objectId": str
        key "userPrincipalName": str
        email: str
        name: str
        objectId: str
        userPrincipalName: str


    class azure.mgmt.securityinsight.types.CodelessApiPollingDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.API_POLLING]]
        key "name": str
        key "properties": ForwardRef('ApiPollingParameters', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.API_POLLING]
        name: str
        properties: ApiPollingParameters
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.CodelessConnectorPollingAuthProperties(TypedDict, total=False):
        key "apiKeyIdentifier": str
        key "apiKeyName": str
        key "authType": Required[str]
        key "authorizationEndpoint": str
        key "authorizationEndpointQueryParameters": Any
        key "flowName": str
        key "isApiKeyInPostPayload": str
        key "isClientSecretInHeader": bool
        key "redirectionEndpoint": str
        key "scope": str
        key "tokenEndpoint": str
        key "tokenEndpointHeaders": Any
        key "tokenEndpointQueryParameters": Any
        apiKeyIdentifier: str
        apiKeyName: str
        authType: str
        authorizationEndpoint: str
        authorizationEndpointQueryParameters: Any
        flowName: str
        isApiKeyInPostPayload: str
        isClientSecretInHeader: bool
        redirectionEndpoint: str
        scope: str
        tokenEndpoint: str
        tokenEndpointHeaders: Any
        tokenEndpointQueryParameters: Any


    class azure.mgmt.securityinsight.types.CodelessConnectorPollingConfigProperties(TypedDict, total=False):
        key "auth": Required[CodelessConnectorPollingAuthProperties]
        key "isActive": bool
        key "paging": ForwardRef('CodelessConnectorPollingPagingProperties', module='types')
        key "request": Required[CodelessConnectorPollingRequestProperties]
        key "response": ForwardRef('CodelessConnectorPollingResponseProperties', module='types')
        auth: CodelessConnectorPollingAuthProperties
        isActive: bool
        paging: CodelessConnectorPollingPagingProperties
        request: CodelessConnectorPollingRequestProperties
        response: CodelessConnectorPollingResponseProperties


    class azure.mgmt.securityinsight.types.CodelessConnectorPollingPagingProperties(TypedDict, total=False):
        key "nextPageParaName": str
        key "nextPageTokenJsonPath": str
        key "pageCountAttributePath": str
        key "pageSize": int
        key "pageSizeParaName": str
        key "pageTimeStampAttributePath": str
        key "pageTotalCountAttributePath": str
        key "pagingType": Required[str]
        key "searchTheLatestTimeStampFromEventsList": str
        nextPageParaName: str
        nextPageTokenJsonPath: str
        pageCountAttributePath: str
        pageSize: int
        pageSizeParaName: str
        pageTimeStampAttributePath: str
        pageTotalCountAttributePath: str
        pagingType: str
        searchTheLatestTimeStampFromEventsList: str


    class azure.mgmt.securityinsight.types.CodelessConnectorPollingRequestProperties(TypedDict, total=False):
        key "apiEndpoint": Required[str]
        key "endTimeAttributeName": str
        key "headers": Any
        key "httpMethod": Required[str]
        key "queryParameters": Any
        key "queryParametersTemplate": str
        key "queryTimeFormat": Required[str]
        key "queryWindowInMin": Required[int]
        key "rateLimitQps": int
        key "retryCount": int
        key "startTimeAttributeName": str
        key "timeoutInSeconds": int
        apiEndpoint: str
        endTimeAttributeName: str
        headers: Any
        httpMethod: str
        queryParameters: Any
        queryParametersTemplate: str
        queryTimeFormat: str
        queryWindowInMin: int
        rateLimitQps: int
        retryCount: int
        startTimeAttributeName: str
        timeoutInSeconds: int


    class azure.mgmt.securityinsight.types.CodelessConnectorPollingResponseProperties(TypedDict, total=False):
        key "eventsJsonPaths": Required[list[str]]
        key "isGzipCompressed": bool
        key "successStatusJsonPath": str
        key "successStatusValue": str
        eventsJsonPaths: list[str]
        isGzipCompressed: bool
        successStatusJsonPath: str
        successStatusValue: str


    class azure.mgmt.securityinsight.types.CodelessParameters(TypedDict, total=False):
        key "connectorUiConfig": ForwardRef('CodelessUiConnectorConfigProperties', module='types')
        connectorUiConfig: CodelessUiConnectorConfigProperties


    class azure.mgmt.securityinsight.types.CodelessUiConnectorConfigProperties(TypedDict, total=False):
        key "availability": Required[Availability]
        key "connectivityCriteria": Required[list[CodelessUiConnectorConfigPropertiesConnectivityCriteriaItem]]
        key "customImage": str
        key "dataTypes": Required[list[CodelessUiConnectorConfigPropertiesDataTypesItem]]
        key "descriptionMarkdown": Required[str]
        key "graphQueries": Required[list[CodelessUiConnectorConfigPropertiesGraphQueriesItem]]
        key "graphQueriesTableName": Required[str]
        key "instructionSteps": Required[list[CodelessUiConnectorConfigPropertiesInstructionStepsItem]]
        key "permissions": Required[Permissions]
        key "publisher": Required[str]
        key "sampleQueries": Required[list[CodelessUiConnectorConfigPropertiesSampleQueriesItem]]
        key "title": Required[str]
        availability: Availability
        connectivityCriteria: list[CodelessUiConnectorConfigPropertiesConnectivityCriteriaItem]
        customImage: str
        dataTypes: list[CodelessUiConnectorConfigPropertiesDataTypesItem]
        descriptionMarkdown: str
        graphQueries: list[CodelessUiConnectorConfigPropertiesGraphQueriesItem]
        graphQueriesTableName: str
        instructionSteps: list[CodelessUiConnectorConfigPropertiesInstructionStepsItem]
        permissions: Permissions
        publisher: str
        sampleQueries: list[CodelessUiConnectorConfigPropertiesSampleQueriesItem]
        title: str


    class azure.mgmt.securityinsight.types.CodelessUiConnectorConfigPropertiesConnectivityCriteriaItem(ConnectivityCriteria):
        key "type": Union[str, ConnectivityType]
        type: Union[str, ConnectivityType]
        value: list[str]


    class azure.mgmt.securityinsight.types.CodelessUiConnectorConfigPropertiesDataTypesItem(LastDataReceivedDataType):
        key "lastDataReceivedQuery": str
        key "name": str
        lastDataReceivedQuery: str
        name: str


    class azure.mgmt.securityinsight.types.CodelessUiConnectorConfigPropertiesGraphQueriesItem(GraphQueries):
        key "baseQuery": str
        key "legend": str
        key "metricName": str
        baseQuery: str
        legend: str
        metricName: str


    class azure.mgmt.securityinsight.types.CodelessUiConnectorConfigPropertiesInstructionStepsItem(InstructionSteps):
        key "description": str
        key "title": str
        description: str
        instructions: list[InstructionStepsInstructionsItem]
        title: str


    class azure.mgmt.securityinsight.types.CodelessUiConnectorConfigPropertiesSampleQueriesItem(SampleQueries):
        key "description": str
        key "query": str
        description: str
        query: str


    class azure.mgmt.securityinsight.types.CodelessUiDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.GENERIC_UI]]
        key "name": str
        key "properties": ForwardRef('CodelessParameters', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.GENERIC_UI]
        name: str
        properties: CodelessParameters
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.ConditionClause(TypedDict, total=False):
        key "clauseConnective": Union[str, Connective]
        key "field": Required[str]
        key "operator": Required[Union[str, Operator]]
        key "values": Required[list[str]]
        clauseConnective: Union[str, Connective]
        field: str
        operator: Union[str, Operator]
        values: list[str]


    class azure.mgmt.securityinsight.types.ConditionProperties(TypedDict, total=False):
        key "clauses": Required[list[ConditionClause]]
        key "conditionConnective": Union[str, Connective]
        key "stixObjectType": str
        clauses: list[ConditionClause]
        conditionConnective: Union[str, Connective]
        stixObjectType: str


    class azure.mgmt.securityinsight.types.ConditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "Boolean"
        PROPERTY = "Property"
        PROPERTY_ARRAY = "PropertyArray"
        PROPERTY_ARRAY_CHANGED = "PropertyArrayChanged"
        PROPERTY_CHANGED = "PropertyChanged"


    class azure.mgmt.securityinsight.types.ConnectivityCriteria(TypedDict, total=False):
        key "type": Union[str, ConnectivityType]
        type: Union[str, ConnectivityType]
        value: list[str]


    class azure.mgmt.securityinsight.types.ConnectivityCriterion(TypedDict, total=False):
        key "type": Required[str]
        type: str
        value: list[str]


    class azure.mgmt.securityinsight.types.ConnectorDataType(TypedDict, total=False):
        key "lastDataReceivedQuery": Required[str]
        key "name": Required[str]
        lastDataReceivedQuery: str
        name: str


    class azure.mgmt.securityinsight.types.ConnectorDefinitionsAvailability(TypedDict, total=False):
        key "isPreview": bool
        key "status": int
        isPreview: bool
        status: int


    class azure.mgmt.securityinsight.types.ConnectorDefinitionsPermissions(TypedDict, total=False):
        customs: list[CustomPermissionDetails]
        licenses: list[str]
        resourceProvider: list[ConnectorDefinitionsResourceProvider]
        tenant: list[str]


    class azure.mgmt.securityinsight.types.ConnectorDefinitionsResourceProvider(TypedDict, total=False):
        key "permissionsDisplayText": Required[str]
        key "provider": Required[str]
        key "providerDisplayName": Required[str]
        key "requiredPermissions": Required[ResourceProviderRequiredPermissions]
        key "scope": Required[Union[str, ProviderPermissionsScope]]
        permissionsDisplayText: str
        provider: str
        providerDisplayName: str
        requiredPermissions: ResourceProviderRequiredPermissions
        scope: Union[str, ProviderPermissionsScope]


    class azure.mgmt.securityinsight.types.ConnectorInstructionModelBase(TypedDict, total=False):
        key "parameters": Any
        key "type": Required[Union[str, SettingType]]
        parameters: Any
        type: Union[str, SettingType]


    class azure.mgmt.securityinsight.types.CountQuery(TypedDict, total=False):
        key "properties": ForwardRef('QueryProperties', module='types')
        properties: QueryProperties


    class azure.mgmt.securityinsight.types.CustomEntityQuery(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[CustomEntityQueryKind.ACTIVITY]]
        key "name": str
        key "properties": ForwardRef('ActivityEntityQueriesProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[CustomEntityQueryKind.ACTIVITY]
        name: str
        properties: ActivityEntityQueriesProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.CustomEntityQueryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY = "Activity"


    class azure.mgmt.securityinsight.types.CustomPermissionDetails(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        description: str
        name: str


    class azure.mgmt.securityinsight.types.CustomizableConnectionsConfig(TypedDict, total=False):
        key "templateSpecName": Required[str]
        key "templateSpecVersion": Required[str]
        templateSpecName: str
        templateSpecVersion: str


    class azure.mgmt.securityinsight.types.CustomizableConnectorDefinition(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorDefinitionKind.CUSTOMIZABLE]]
        key "name": str
        key "properties": ForwardRef('CustomizableConnectorDefinitionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorDefinitionKind.CUSTOMIZABLE]
        name: str
        properties: CustomizableConnectorDefinitionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.CustomizableConnectorDefinitionProperties(TypedDict, total=False):
        key "connectionsConfig": ForwardRef('CustomizableConnectionsConfig', module='types')
        key "connectorUiConfig": Required[CustomizableConnectorUiConfig]
        key "createdTimeUtc": str
        key "lastModifiedUtc": str
        connectionsConfig: CustomizableConnectionsConfig
        connectorUiConfig: CustomizableConnectorUiConfig
        createdTimeUtc: str
        lastModifiedUtc: str


    class azure.mgmt.securityinsight.types.CustomizableConnectorUiConfig(TypedDict, total=False):
        key "availability": ForwardRef('ConnectorDefinitionsAvailability', module='types')
        key "connectivityCriteria": Required[list[ConnectivityCriterion]]
        key "dataTypes": Required[list[ConnectorDataType]]
        key "descriptionMarkdown": Required[str]
        key "graphQueries": Required[list[GraphQuery]]
        key "id": str
        key "instructionSteps": Required[list[InstructionStep]]
        key "isConnectivityCriteriasMatchSome": bool
        key "logo": str
        key "permissions": Required[ConnectorDefinitionsPermissions]
        key "publisher": Required[str]
        key "title": Required[str]
        availability: ConnectorDefinitionsAvailability
        connectivityCriteria: list[ConnectivityCriterion]
        dataTypes: list[ConnectorDataType]
        descriptionMarkdown: str
        graphQueries: list[GraphQuery]
        id: str
        instructionSteps: list[InstructionStep]
        isConnectivityCriteriasMatchSome: bool
        logo: str
        permissions: ConnectorDefinitionsPermissions
        publisher: str
        title: str


    class azure.mgmt.securityinsight.types.Customs(CustomsPermission):
        key "description": str
        key "name": str
        description: str
        name: str


    class azure.mgmt.securityinsight.types.CustomsPermission(TypedDict, total=False):
        key "description": str
        key "name": str
        description: str
        name: str


    class azure.mgmt.securityinsight.types.DCRConfiguration(TypedDict, total=False):
        key "dataCollectionEndpoint": Required[str]
        key "dataCollectionRuleImmutableId": Required[str]
        key "streamName": Required[str]
        dataCollectionEndpoint: str
        dataCollectionRuleImmutableId: str
        streamName: str


    class azure.mgmt.securityinsight.types.DataConnectorConnectBody(TypedDict, total=False):
        key "apiKey": str
        key "authorizationCode": str
        key "clientId": str
        key "clientSecret": str
        key "dataCollectionEndpoint": str
        key "dataCollectionRuleImmutableId": str
        key "kind": Union[str, ConnectAuthKind]
        key "outputStream": str
        key "password": str
        key "userName": str
        apiKey: str
        authorizationCode: str
        clientId: str
        clientSecret: str
        dataCollectionEndpoint: str
        dataCollectionRuleImmutableId: str
        kind: Union[str, ConnectAuthKind]
        outputStream: str
        password: str
        requestConfigUserInputValues: list[Any]
        userName: str


    class azure.mgmt.securityinsight.types.DataConnectorDataTypeCommon(TypedDict, total=False):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.DataConnectorDefinition(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorDefinitionKind.CUSTOMIZABLE]]
        key "name": str
        key "properties": ForwardRef('CustomizableConnectorDefinitionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorDefinitionKind.CUSTOMIZABLE]
        name: str
        properties: CustomizableConnectorDefinitionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.DataConnectorDefinitionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMIZABLE = "Customizable"


    class azure.mgmt.securityinsight.types.DataConnectorKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMAZON_WEB_SERVICES_CLOUD_TRAIL = "AmazonWebServicesCloudTrail"
        AMAZON_WEB_SERVICES_S3 = "AmazonWebServicesS3"
        API_POLLING = "APIPolling"
        AZURE_ACTIVE_DIRECTORY = "AzureActiveDirectory"
        AZURE_ADVANCED_THREAT_PROTECTION = "AzureAdvancedThreatProtection"
        AZURE_SECURITY_CENTER = "AzureSecurityCenter"
        DYNAMICS365 = "Dynamics365"
        GCP = "GCP"
        GENERIC_UI = "GenericUI"
        IOT = "IOT"
        MICROSOFT_CLOUD_APP_SECURITY = "MicrosoftCloudAppSecurity"
        MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION = "MicrosoftDefenderAdvancedThreatProtection"
        MICROSOFT_PURVIEW_INFORMATION_PROTECTION = "MicrosoftPurviewInformationProtection"
        MICROSOFT_THREAT_INTELLIGENCE = "MicrosoftThreatIntelligence"
        MICROSOFT_THREAT_PROTECTION = "MicrosoftThreatProtection"
        OFFICE365 = "Office365"
        OFFICE365_PROJECT = "Office365Project"
        OFFICE_ATP = "OfficeATP"
        OFFICE_IRM = "OfficeIRM"
        OFFICE_POWER_BI = "OfficePowerBI"
        PREMIUM_MICROSOFT_DEFENDER_FOR_THREAT_INTELLIGENCE = "PremiumMicrosoftDefenderForThreatIntelligence"
        PURVIEW_AUDIT = "PurviewAudit"
        REST_API_POLLER = "RestApiPoller"
        THREAT_INTELLIGENCE = "ThreatIntelligence"
        THREAT_INTELLIGENCE_TAXII = "ThreatIntelligenceTaxii"


    class azure.mgmt.securityinsight.types.DataConnectorTenantId(TypedDict, total=False):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.DataConnectorWithAlertsProperties(TypedDict, total=False):
        key "dataTypes": ForwardRef('AlertsDataTypeOfDataConnector', module='types')
        dataTypes: AlertsDataTypeOfDataConnector


    class azure.mgmt.securityinsight.types.Deployment(TypedDict, total=False):
        key "deploymentId": str
        key "deploymentLogsUrl": str
        key "deploymentResult": Union[str, DeploymentResult]
        key "deploymentState": Union[str, DeploymentState]
        key "deploymentTime": str
        deploymentId: str
        deploymentLogsUrl: str
        deploymentResult: Union[str, DeploymentResult]
        deploymentState: Union[str, DeploymentState]
        deploymentTime: str


    class azure.mgmt.securityinsight.types.DeploymentInfo(TypedDict, total=False):
        key "deployment": ForwardRef('Deployment', module='types')
        key "deploymentFetchStatus": Union[str, DeploymentFetchStatus]
        key "message": str
        deployment: Deployment
        deploymentFetchStatus: Union[str, DeploymentFetchStatus]
        message: str


    class azure.mgmt.securityinsight.types.Dynamics365CheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.DYNAMICS365]]
        key "properties": ForwardRef('Dynamics365CheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.DYNAMICS365]
        properties: Dynamics365CheckRequirementsProperties


    class azure.mgmt.securityinsight.types.Dynamics365CheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.Dynamics365DataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.DYNAMICS365]]
        key "name": str
        key "properties": ForwardRef('Dynamics365DataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.DYNAMICS365]
        name: str
        properties: Dynamics365DataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.Dynamics365DataConnectorDataTypes(TypedDict, total=False):
        key "dynamics365CdsActivities": Required[Dynamics365DataConnectorDataTypesDynamics365CdsActivities]
        dynamics365CdsActivities: Dynamics365DataConnectorDataTypesDynamics365CdsActivities


    class azure.mgmt.securityinsight.types.Dynamics365DataConnectorDataTypesDynamics365CdsActivities(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.Dynamics365DataConnectorProperties(DataConnectorTenantId):
        key "dataTypes": Required[Dynamics365DataConnectorDataTypes]
        key "tenantId": Required[str]
        dataTypes: Dynamics365DataConnectorDataTypes
        tenantId: str


    class azure.mgmt.securityinsight.types.EnrichmentDomainBody(TypedDict, total=False):
        key "domain": str
        domain: str


    class azure.mgmt.securityinsight.types.EnrichmentIpAddressBody(TypedDict, total=False):
        key "ipAddress": str
        ipAddress: str


    class azure.mgmt.securityinsight.types.EntityAnalytics(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[SettingKind.ENTITY_ANALYTICS]]
        key "name": str
        key "properties": ForwardRef('EntityAnalyticsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[SettingKind.ENTITY_ANALYTICS]
        name: str
        properties: EntityAnalyticsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.EntityAnalyticsProperties(TypedDict, total=False):
        entityProviders: list[Union[str, EntityProviders]]


    class azure.mgmt.securityinsight.types.EntityCommonProperties(TypedDict, total=False):
        key "friendlyName": str
        additionalData: dict[str, Any]
        friendlyName: str


    class azure.mgmt.securityinsight.types.EntityExpandParameters(TypedDict, total=False):
        key "endTime": str
        key "expansionId": str
        key "startTime": str
        endTime: str
        expansionId: str
        startTime: str


    class azure.mgmt.securityinsight.types.EntityFieldMapping(TypedDict, total=False):
        key "identifier": str
        key "value": str
        identifier: str
        value: str


    class azure.mgmt.securityinsight.types.EntityGetInsightsParameters(TypedDict, total=False):
        key "addDefaultExtendedTimeRange": bool
        key "endTime": Required[str]
        key "startTime": Required[str]
        addDefaultExtendedTimeRange: bool
        endTime: str
        insightQueryIds: list[str]
        startTime: str


    class azure.mgmt.securityinsight.types.EntityManualTriggerRequestBody(TypedDict, total=False):
        key "incidentArmId": str
        key "logicAppsResourceId": Required[str]
        key "tenantId": str
        incidentArmId: str
        logicAppsResourceId: str
        tenantId: str


    class azure.mgmt.securityinsight.types.EntityMapping(TypedDict, total=False):
        key "entityType": Union[str, EntityMappingType]
        entityType: Union[str, EntityMappingType]
        fieldMappings: list[FieldMapping]


    class azure.mgmt.securityinsight.types.EntityTimelineParameters(TypedDict, total=False):
        key "endTime": Required[str]
        key "numberOfBucket": int
        key "startTime": Required[str]
        endTime: str
        kinds: list[Union[str, EntityTimelineKind]]
        numberOfBucket: int
        startTime: str


    class azure.mgmt.securityinsight.types.EventGroupingSettings(TypedDict, total=False):
        key "aggregationKind": Union[str, EventGroupingAggregationKind]
        aggregationKind: Union[str, EventGroupingAggregationKind]


    class azure.mgmt.securityinsight.types.EyesOn(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[SettingKind.EYES_ON]]
        key "name": str
        key "properties": ForwardRef('EyesOnSettingsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[SettingKind.EYES_ON]
        name: str
        properties: EyesOnSettingsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.EyesOnSettingsProperties(TypedDict, total=False):
        key "isEnabled": bool
        isEnabled: bool


    class azure.mgmt.securityinsight.types.FieldMapping(TypedDict, total=False):
        key "columnName": str
        key "identifier": str
        columnName: str
        identifier: str


    class azure.mgmt.securityinsight.types.FileImport(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FileImportProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FileImportProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.FileImportProperties(TypedDict, total=False):
        key "contentType": Required[Union[str, FileImportContentType]]
        key "createdTimeUTC": str
        key "errorFile": ForwardRef('FileMetadata', module='types')
        key "filesValidUntilTimeUTC": str
        key "importFile": Required[FileMetadata]
        key "importValidUntilTimeUTC": str
        key "ingestedRecordCount": int
        key "ingestionMode": Required[Union[str, IngestionMode]]
        key "source": Required[str]
        key "state": Union[str, FileImportState]
        key "totalRecordCount": int
        key "validRecordCount": int
        contentType: Union[str, FileImportContentType]
        createdTimeUTC: str
        errorFile: FileMetadata
        errorsPreview: list[ValidationError]
        filesValidUntilTimeUTC: str
        importFile: FileMetadata
        importValidUntilTimeUTC: str
        ingestedRecordCount: int
        ingestionMode: Union[str, IngestionMode]
        source: str
        state: Union[str, FileImportState]
        totalRecordCount: int
        validRecordCount: int


    class azure.mgmt.securityinsight.types.FileMetadata(TypedDict, total=False):
        key "deleteStatus": Union[str, DeleteStatus]
        key "fileContentUri": str
        key "fileFormat": Union[str, FileFormat]
        key "fileName": str
        key "fileSize": int
        deleteStatus: Union[str, DeleteStatus]
        fileContentUri: str
        fileFormat: Union[str, FileFormat]
        fileName: str
        fileSize: int


    class azure.mgmt.securityinsight.types.FusionAlertRule(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[AlertRuleKind.FUSION]]
        key "name": str
        key "properties": ForwardRef('FusionAlertRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[AlertRuleKind.FUSION]
        name: str
        properties: FusionAlertRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.FusionAlertRuleProperties(TypedDict, total=False):
        key "alertRuleTemplateName": Required[str]
        key "description": str
        key "displayName": str
        key "enabled": Required[bool]
        key "lastModifiedUtc": str
        key "severity": Union[str, AlertSeverity]
        alertRuleTemplateName: str
        description: str
        displayName: str
        enabled: bool
        lastModifiedUtc: str
        scenarioExclusionPatterns: list[FusionScenarioExclusionPattern]
        severity: Union[str, AlertSeverity]
        sourceSettings: list[FusionSourceSettings]
        subTechniques: list[str]
        tactics: list[Union[str, AttackTactic]]
        techniques: list[str]


    class azure.mgmt.securityinsight.types.FusionScenarioExclusionPattern(TypedDict, total=False):
        key "dateAddedInUTC": Required[str]
        key "exclusionPattern": Required[str]
        dateAddedInUTC: str
        exclusionPattern: str


    class azure.mgmt.securityinsight.types.FusionSourceSettings(TypedDict, total=False):
        key "enabled": Required[bool]
        key "sourceName": Required[str]
        enabled: bool
        sourceName: str
        sourceSubTypes: list[FusionSourceSubTypeSetting]


    class azure.mgmt.securityinsight.types.FusionSourceSubTypeSetting(TypedDict, total=False):
        key "enabled": Required[bool]
        key "severityFilters": Required[FusionSubTypeSeverityFilter]
        key "sourceSubTypeDisplayName": str
        key "sourceSubTypeName": Required[str]
        enabled: bool
        severityFilters: FusionSubTypeSeverityFilter
        sourceSubTypeDisplayName: str
        sourceSubTypeName: str


    class azure.mgmt.securityinsight.types.FusionSubTypeSeverityFilter(TypedDict, total=False):
        key "isSupported": bool
        filters: list[FusionSubTypeSeverityFiltersItem]
        isSupported: bool


    class azure.mgmt.securityinsight.types.FusionSubTypeSeverityFiltersItem(TypedDict, total=False):
        key "enabled": Required[bool]
        key "severity": Required[Union[str, AlertSeverity]]
        enabled: bool
        severity: Union[str, AlertSeverity]


    class azure.mgmt.securityinsight.types.GCPAuthModel(TypedDict, total=False):
        key "projectNumber": Required[str]
        key "serviceAccountEmail": Required[str]
        key "type": Required[Literal[CcpAuthType.GCP]]
        key "workloadIdentityProviderId": Required[str]
        projectNumber: str
        serviceAccountEmail: str
        type: Literal[CcpAuthType.GCP]
        workloadIdentityProviderId: str


    class azure.mgmt.securityinsight.types.GCPAuthProperties(TypedDict, total=False):
        key "projectNumber": Required[str]
        key "serviceAccountEmail": Required[str]
        key "workloadIdentityProviderId": Required[str]
        projectNumber: str
        serviceAccountEmail: str
        workloadIdentityProviderId: str


    class azure.mgmt.securityinsight.types.GCPDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.GCP]]
        key "name": str
        key "properties": ForwardRef('GCPDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.GCP]
        name: str
        properties: GCPDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.GCPDataConnectorProperties(TypedDict, total=False):
        key "auth": Required[GCPAuthProperties]
        key "connectorDefinitionName": Required[str]
        key "dcrConfig": ForwardRef('DCRConfiguration', module='types')
        key "request": Required[GCPRequestProperties]
        auth: GCPAuthProperties
        connectorDefinitionName: str
        dcrConfig: DCRConfiguration
        request: GCPRequestProperties


    class azure.mgmt.securityinsight.types.GCPRequestProperties(TypedDict, total=False):
        key "projectId": Required[str]
        key "subscriptionNames": Required[list[str]]
        projectId: str
        subscriptionNames: list[str]


    class azure.mgmt.securityinsight.types.GenericBlobSbsAuthModel(TypedDict, total=False):
        key "type": Required[Literal[CcpAuthType.SERVICE_BUS]]
        credentialsConfig: dict[str, str]
        storageAccountCredentialsConfig: dict[str, str]
        type: Literal[CcpAuthType.SERVICE_BUS]


    class azure.mgmt.securityinsight.types.GitHubAuthModel(TypedDict, total=False):
        key "installationId": str
        key "type": Required[Literal[CcpAuthType.GIT_HUB]]
        installationId: str
        type: Literal[CcpAuthType.GIT_HUB]


    class azure.mgmt.securityinsight.types.GitHubResourceInfo(TypedDict, total=False):
        key "appInstallationId": str
        appInstallationId: str


    class azure.mgmt.securityinsight.types.GraphQueries(TypedDict, total=False):
        key "baseQuery": str
        key "legend": str
        key "metricName": str
        baseQuery: str
        legend: str
        metricName: str


    class azure.mgmt.securityinsight.types.GraphQuery(TypedDict, total=False):
        key "baseQuery": Required[str]
        key "legend": Required[str]
        key "metricName": Required[str]
        baseQuery: str
        legend: str
        metricName: str


    class azure.mgmt.securityinsight.types.GroupingConfiguration(TypedDict, total=False):
        key "enabled": Required[bool]
        key "lookbackDuration": Required[str]
        key "matchingMethod": Required[Union[str, MatchingMethod]]
        key "reopenClosedIncident": Required[bool]
        enabled: bool
        groupByAlertDetails: list[Union[str, AlertDetail]]
        groupByCustomDetails: list[str]
        groupByEntities: list[Union[str, EntityMappingType]]
        lookbackDuration: str
        matchingMethod: Union[str, MatchingMethod]
        reopenClosedIncident: bool


    class azure.mgmt.securityinsight.types.Hunt(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('HuntProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: HuntProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.HuntComment(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('HuntCommentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: HuntCommentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.HuntCommentProperties(TypedDict, total=False):
        key "message": Required[str]
        message: str


    class azure.mgmt.securityinsight.types.HuntOwner(TypedDict, total=False):
        key "assignedTo": str
        key "email": str
        key "objectId": Optional[str]
        key "ownerType": Union[str, OwnerType]
        key "userPrincipalName": str
        assignedTo: str
        email: str
        objectId: str
        ownerType: Union[str, OwnerType]
        userPrincipalName: str


    class azure.mgmt.securityinsight.types.HuntProperties(TypedDict, total=False):
        key "description": Required[str]
        key "displayName": Required[str]
        key "hypothesisStatus": Union[str, HypothesisStatus]
        key "owner": ForwardRef('HuntOwner', module='types')
        key "status": Union[str, Status]
        attackTactics: list[Union[str, AttackTactic]]
        attackTechniques: list[str]
        description: str
        displayName: str
        hypothesisStatus: Union[str, HypothesisStatus]
        labels: list[str]
        owner: HuntOwner
        status: Union[str, Status]


    class azure.mgmt.securityinsight.types.HuntRelation(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('HuntRelationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: HuntRelationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.HuntRelationProperties(TypedDict, total=False):
        key "relatedResourceId": Required[str]
        key "relatedResourceKind": str
        key "relatedResourceName": str
        key "relationType": str
        labels: list[str]
        relatedResourceId: str
        relatedResourceKind: str
        relatedResourceName: str
        relationType: str


    class azure.mgmt.securityinsight.types.Incident(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('IncidentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: IncidentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.IncidentAdditionalData(TypedDict, total=False):
        key "alertsCount": int
        key "bookmarksCount": int
        key "commentsCount": int
        key "mergedIncidentNumber": str
        key "mergedIncidentUrl": str
        key "providerIncidentUrl": str
        alertProductNames: list[str]
        alertsCount: int
        bookmarksCount: int
        commentsCount: int
        mergedIncidentNumber: str
        mergedIncidentUrl: str
        providerIncidentUrl: str
        tactics: list[Union[str, AttackTactic]]
        techniques: list[str]


    class azure.mgmt.securityinsight.types.IncidentComment(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('IncidentCommentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: IncidentCommentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.IncidentCommentProperties(TypedDict, total=False):
        key "author": ForwardRef('ClientInfo', module='types')
        key "createdTimeUtc": str
        key "lastModifiedTimeUtc": str
        key "message": Required[str]
        author: ClientInfo
        createdTimeUtc: str
        lastModifiedTimeUtc: str
        message: str


    class azure.mgmt.securityinsight.types.IncidentConfiguration(TypedDict, total=False):
        key "createIncident": Required[bool]
        key "groupingConfiguration": ForwardRef('GroupingConfiguration', module='types')
        createIncident: bool
        groupingConfiguration: GroupingConfiguration


    class azure.mgmt.securityinsight.types.IncidentInfo(TypedDict, total=False):
        key "incidentId": str
        key "relationName": str
        key "severity": Union[str, IncidentSeverity]
        key "title": str
        incidentId: str
        relationName: str
        severity: Union[str, IncidentSeverity]
        title: str


    class azure.mgmt.securityinsight.types.IncidentLabel(TypedDict, total=False):
        key "labelName": Required[str]
        key "labelType": Union[str, IncidentLabelType]
        labelName: str
        labelType: Union[str, IncidentLabelType]


    class azure.mgmt.securityinsight.types.IncidentOwnerInfo(TypedDict, total=False):
        key "assignedTo": str
        key "email": str
        key "objectId": str
        key "ownerType": Union[str, OwnerType]
        key "userPrincipalName": str
        assignedTo: str
        email: str
        objectId: str
        ownerType: Union[str, OwnerType]
        userPrincipalName: str


    class azure.mgmt.securityinsight.types.IncidentProperties(TypedDict, total=False):
        key "additionalData": ForwardRef('IncidentAdditionalData', module='types')
        key "classification": Union[str, IncidentClassification]
        key "classificationComment": str
        key "classificationReason": Union[str, IncidentClassificationReason]
        key "createdTimeUtc": str
        key "description": str
        key "firstActivityTimeUtc": str
        key "incidentNumber": int
        key "incidentUrl": str
        key "lastActivityTimeUtc": str
        key "lastModifiedTimeUtc": str
        key "owner": ForwardRef('IncidentOwnerInfo', module='types')
        key "providerIncidentId": str
        key "providerName": str
        key "severity": Required[Union[str, IncidentSeverity]]
        key "status": Required[Union[str, IncidentStatus]]
        key "teamInformation": ForwardRef('TeamInformation', module='types')
        key "title": Required[str]
        additionalData: IncidentAdditionalData
        classification: Union[str, IncidentClassification]
        classificationComment: str
        classificationReason: Union[str, IncidentClassificationReason]
        createdTimeUtc: str
        description: str
        firstActivityTimeUtc: str
        incidentNumber: int
        incidentUrl: str
        labels: list[IncidentLabel]
        lastActivityTimeUtc: str
        lastModifiedTimeUtc: str
        owner: IncidentOwnerInfo
        providerIncidentId: str
        providerName: str
        relatedAnalyticRuleIds: list[str]
        severity: Union[str, IncidentSeverity]
        status: Union[str, IncidentStatus]
        teamInformation: TeamInformation
        title: str


    class azure.mgmt.securityinsight.types.IncidentPropertiesAction(TypedDict, total=False):
        key "classification": Union[str, IncidentClassification]
        key "classificationComment": str
        key "classificationReason": Union[str, IncidentClassificationReason]
        key "owner": ForwardRef('IncidentOwnerInfo', module='types')
        key "severity": Union[str, IncidentSeverity]
        key "status": Union[str, IncidentStatus]
        classification: Union[str, IncidentClassification]
        classificationComment: str
        classificationReason: Union[str, IncidentClassificationReason]
        labels: list[IncidentLabel]
        owner: IncidentOwnerInfo
        severity: Union[str, IncidentSeverity]
        status: Union[str, IncidentStatus]


    class azure.mgmt.securityinsight.types.IncidentTask(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": Required[IncidentTaskProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: IncidentTaskProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.IncidentTaskProperties(TypedDict, total=False):
        key "createdBy": ForwardRef('ClientInfo', module='types')
        key "createdTimeUtc": str
        key "description": str
        key "lastModifiedBy": ForwardRef('ClientInfo', module='types')
        key "lastModifiedTimeUtc": str
        key "status": Required[Union[str, IncidentTaskStatus]]
        key "title": Required[str]
        createdBy: ClientInfo
        createdTimeUtc: str
        description: str
        lastModifiedBy: ClientInfo
        lastModifiedTimeUtc: str
        status: Union[str, IncidentTaskStatus]
        title: str


    class azure.mgmt.securityinsight.types.InstructionStep(TypedDict, total=False):
        key "description": str
        key "title": str
        description: str
        innerSteps: list[InstructionStep]
        instructions: list[InstructionStepDetails]
        title: str


    class azure.mgmt.securityinsight.types.InstructionStepDetails(TypedDict, total=False):
        key "parameters": Required[Any]
        key "type": Required[str]
        parameters: Any
        type: str


    class azure.mgmt.securityinsight.types.InstructionSteps(TypedDict, total=False):
        key "description": str
        key "title": str
        description: str
        instructions: list[InstructionStepsInstructionsItem]
        title: str


    class azure.mgmt.securityinsight.types.InstructionStepsInstructionsItem(ConnectorInstructionModelBase):
        key "parameters": Any
        key "type": Required[Union[str, SettingType]]
        parameters: Any
        type: Union[str, SettingType]


    class azure.mgmt.securityinsight.types.IoTCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.IOT]]
        key "properties": ForwardRef('IoTCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.IOT]
        properties: IoTCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.IoTCheckRequirementsProperties(TypedDict, total=False):
        key "subscriptionId": str
        subscriptionId: str


    class azure.mgmt.securityinsight.types.IoTDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.IOT]]
        key "name": str
        key "properties": ForwardRef('IoTDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.IOT]
        name: str
        properties: IoTDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.IoTDataConnectorProperties(DataConnectorWithAlertsProperties):
        key "dataTypes": ForwardRef('AlertsDataTypeOfDataConnector', module='types')
        key "subscriptionId": str
        dataTypes: AlertsDataTypeOfDataConnector
        subscriptionId: str


    class azure.mgmt.securityinsight.types.JwtAuthModel(TypedDict, total=False):
        key "isCredentialsInHeaders": Optional[bool]
        key "isJsonRequest": Optional[bool]
        key "password": Required[dict[str, str]]
        key "requestTimeoutInSeconds": int
        key "tokenEndpoint": Required[str]
        key "type": Required[Literal[CcpAuthType.JWT_TOKEN]]
        key "userName": Required[dict[str, str]]
        headers: dict[str, str]
        isCredentialsInHeaders: bool
        isJsonRequest: bool
        password: dict[str, str]
        queryParameters: dict[str, str]
        requestTimeoutInSeconds: int
        tokenEndpoint: str
        type: Literal[CcpAuthType.JWT_TOKEN]
        userName: dict[str, str]


    class azure.mgmt.securityinsight.types.LastDataReceivedDataType(TypedDict, total=False):
        key "lastDataReceivedQuery": str
        key "name": str
        lastDataReceivedQuery: str
        name: str


    class azure.mgmt.securityinsight.types.MCASCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.MICROSOFT_CLOUD_APP_SECURITY]]
        key "properties": ForwardRef('MCASCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.MICROSOFT_CLOUD_APP_SECURITY]
        properties: MCASCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.MCASCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.MCASDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.MICROSOFT_CLOUD_APP_SECURITY]]
        key "name": str
        key "properties": ForwardRef('MCASDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.MICROSOFT_CLOUD_APP_SECURITY]
        name: str
        properties: MCASDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.MCASDataConnectorDataTypes(AlertsDataTypeOfDataConnector):
        key "alerts": Required[DataConnectorDataTypeCommon]
        key "discoveryLogs": ForwardRef('DataConnectorDataTypeCommon', module='types')
        alerts: DataConnectorDataTypeCommon
        discoveryLogs: DataConnectorDataTypeCommon


    class azure.mgmt.securityinsight.types.MCASDataConnectorProperties(DataConnectorTenantId):
        key "dataTypes": Required[MCASDataConnectorDataTypes]
        key "tenantId": Required[str]
        dataTypes: MCASDataConnectorDataTypes
        tenantId: str


    class azure.mgmt.securityinsight.types.MDATPCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION]]
        key "properties": ForwardRef('MDATPCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION]
        properties: MDATPCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.MDATPCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.MDATPDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION]]
        key "name": str
        key "properties": ForwardRef('MDATPDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.MICROSOFT_DEFENDER_ADVANCED_THREAT_PROTECTION]
        name: str
        properties: MDATPDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.MDATPDataConnectorProperties(TypedDict, total=False):
        key "dataTypes": ForwardRef('AlertsDataTypeOfDataConnector', module='types')
        key "tenantId": Required[str]
        dataTypes: AlertsDataTypeOfDataConnector
        tenantId: str


    class azure.mgmt.securityinsight.types.MLBehaviorAnalyticsAlertRule(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[AlertRuleKind.ML_BEHAVIOR_ANALYTICS]]
        key "name": str
        key "properties": ForwardRef('MLBehaviorAnalyticsAlertRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[AlertRuleKind.ML_BEHAVIOR_ANALYTICS]
        name: str
        properties: MLBehaviorAnalyticsAlertRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.MLBehaviorAnalyticsAlertRuleProperties(TypedDict, total=False):
        key "alertRuleTemplateName": Required[str]
        key "description": str
        key "displayName": str
        key "enabled": Required[bool]
        key "lastModifiedUtc": str
        key "severity": Union[str, AlertSeverity]
        alertRuleTemplateName: str
        description: str
        displayName: str
        enabled: bool
        lastModifiedUtc: str
        severity: Union[str, AlertSeverity]
        subTechniques: list[str]
        tactics: list[Union[str, AttackTactic]]
        techniques: list[str]


    class azure.mgmt.securityinsight.types.MSTICheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.MICROSOFT_THREAT_INTELLIGENCE]]
        key "properties": ForwardRef('MSTICheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.MICROSOFT_THREAT_INTELLIGENCE]
        properties: MSTICheckRequirementsProperties


    class azure.mgmt.securityinsight.types.MSTICheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.MSTIDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.MICROSOFT_THREAT_INTELLIGENCE]]
        key "name": str
        key "properties": ForwardRef('MSTIDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.MICROSOFT_THREAT_INTELLIGENCE]
        name: str
        properties: MSTIDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.MSTIDataConnectorDataTypes(TypedDict, total=False):
        key "microsoftEmergingThreatFeed": Required[MSTIDataConnectorDataTypesMicrosoftEmergingThreatFeed]
        microsoftEmergingThreatFeed: MSTIDataConnectorDataTypesMicrosoftEmergingThreatFeed


    class azure.mgmt.securityinsight.types.MSTIDataConnectorDataTypesMicrosoftEmergingThreatFeed(DataConnectorDataTypeCommon):
        key "lookbackPeriod": Required[str]
        key "state": Required[Union[str, DataTypeState]]
        lookbackPeriod: str
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.MSTIDataConnectorProperties(DataConnectorTenantId):
        key "dataTypes": Required[MSTIDataConnectorDataTypes]
        key "tenantId": Required[str]
        dataTypes: MSTIDataConnectorDataTypes
        tenantId: str


    class azure.mgmt.securityinsight.types.MTPCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.MTPDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.MICROSOFT_THREAT_PROTECTION]]
        key "name": str
        key "properties": ForwardRef('MTPDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.MICROSOFT_THREAT_PROTECTION]
        name: str
        properties: MTPDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.MTPDataConnectorDataTypes(TypedDict, total=False):
        key "alerts": ForwardRef('MTPDataConnectorDataTypesAlerts', module='types')
        key "incidents": Required[MTPDataConnectorDataTypesIncidents]
        alerts: MTPDataConnectorDataTypesAlerts
        incidents: MTPDataConnectorDataTypesIncidents


    class azure.mgmt.securityinsight.types.MTPDataConnectorDataTypesAlerts(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.MTPDataConnectorDataTypesIncidents(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.MTPDataConnectorProperties(DataConnectorTenantId):
        key "dataTypes": Required[MTPDataConnectorDataTypes]
        key "filteredProviders": ForwardRef('MtpFilteredProviders', module='types')
        key "tenantId": Required[str]
        dataTypes: MTPDataConnectorDataTypes
        filteredProviders: MtpFilteredProviders
        tenantId: str


    class azure.mgmt.securityinsight.types.ManualTriggerRequestBody(TypedDict, total=False):
        key "logicAppsResourceId": Required[str]
        key "tenantId": str
        logicAppsResourceId: str
        tenantId: str


    class azure.mgmt.securityinsight.types.MetadataAuthor(TypedDict, total=False):
        key "email": str
        key "link": str
        key "name": str
        email: str
        link: str
        name: str


    class azure.mgmt.securityinsight.types.MetadataCategories(TypedDict, total=False):
        domains: list[str]
        verticals: list[str]


    class azure.mgmt.securityinsight.types.MetadataDependencies(TypedDict, total=False):
        key "contentId": str
        key "kind": Union[str, Kind]
        key "name": str
        key "operator": Union[str, MetadataDependencyOperator]
        key "version": str
        contentId: str
        criteria: list[MetadataDependencies]
        kind: Union[str, Kind]
        name: str
        operator: Union[str, MetadataDependencyOperator]
        version: str


    class azure.mgmt.securityinsight.types.MetadataModel(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('MetadataProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: MetadataProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.MetadataPatch(ResourceWithEtag):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('MetadataPropertiesPatch', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: MetadataPropertiesPatch
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.MetadataProperties(TypedDict, total=False):
        key "author": ForwardRef('MetadataAuthor', module='types')
        key "categories": ForwardRef('MetadataCategories', module='types')
        key "contentId": str
        key "contentSchemaVersion": str
        key "customVersion": str
        key "dependencies": ForwardRef('MetadataDependencies', module='types')
        key "firstPublishDate": str
        key "icon": str
        key "kind": Required[str]
        key "lastPublishDate": str
        key "parentId": Required[str]
        key "source": ForwardRef('MetadataSource', module='types')
        key "support": ForwardRef('MetadataSupport', module='types')
        key "version": str
        author: MetadataAuthor
        categories: MetadataCategories
        contentId: str
        contentSchemaVersion: str
        customVersion: str
        dependencies: MetadataDependencies
        firstPublishDate: str
        icon: str
        kind: str
        lastPublishDate: str
        parentId: str
        previewImages: list[str]
        previewImagesDark: list[str]
        providers: list[str]
        source: MetadataSource
        support: MetadataSupport
        threatAnalysisTactics: list[str]
        threatAnalysisTechniques: list[str]
        version: str


    class azure.mgmt.securityinsight.types.MetadataPropertiesPatch(TypedDict, total=False):
        key "author": ForwardRef('MetadataAuthor', module='types')
        key "categories": ForwardRef('MetadataCategories', module='types')
        key "contentId": str
        key "contentSchemaVersion": str
        key "customVersion": str
        key "dependencies": ForwardRef('MetadataDependencies', module='types')
        key "firstPublishDate": str
        key "icon": str
        key "kind": str
        key "lastPublishDate": str
        key "parentId": str
        key "source": ForwardRef('MetadataSource', module='types')
        key "support": ForwardRef('MetadataSupport', module='types')
        key "version": str
        author: MetadataAuthor
        categories: MetadataCategories
        contentId: str
        contentSchemaVersion: str
        customVersion: str
        dependencies: MetadataDependencies
        firstPublishDate: str
        icon: str
        kind: str
        lastPublishDate: str
        parentId: str
        previewImages: list[str]
        previewImagesDark: list[str]
        providers: list[str]
        source: MetadataSource
        support: MetadataSupport
        threatAnalysisTactics: list[str]
        threatAnalysisTechniques: list[str]
        version: str


    class azure.mgmt.securityinsight.types.MetadataSource(TypedDict, total=False):
        key "kind": Required[Union[str, SourceKind]]
        key "name": str
        key "sourceId": str
        kind: Union[str, SourceKind]
        name: str
        sourceId: str


    class azure.mgmt.securityinsight.types.MetadataSupport(TypedDict, total=False):
        key "email": str
        key "link": str
        key "name": str
        key "tier": Required[Union[str, SupportTier]]
        email: str
        link: str
        name: str
        tier: Union[str, SupportTier]


    class azure.mgmt.securityinsight.types.MicrosoftPurviewInformationProtectionCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.MICROSOFT_PURVIEW_INFORMATION_PROTECTION]]
        key "properties": ForwardRef('MicrosoftPurviewInformationProtectionCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.MICROSOFT_PURVIEW_INFORMATION_PROTECTION]
        properties: MicrosoftPurviewInformationProtectionCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.MicrosoftPurviewInformationProtectionCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.MicrosoftPurviewInformationProtectionConnectorDataTypes(TypedDict, total=False):
        key "logs": Required[MicrosoftPurviewInformationProtectionConnectorDataTypesLogs]
        logs: MicrosoftPurviewInformationProtectionConnectorDataTypesLogs


    class azure.mgmt.securityinsight.types.MicrosoftPurviewInformationProtectionConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.MicrosoftPurviewInformationProtectionDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.MICROSOFT_PURVIEW_INFORMATION_PROTECTION]]
        key "name": str
        key "properties": ForwardRef('MicrosoftPurviewInformationProtectionDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.MICROSOFT_PURVIEW_INFORMATION_PROTECTION]
        name: str
        properties: MicrosoftPurviewInformationProtectionDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.MicrosoftPurviewInformationProtectionDataConnectorProperties(DataConnectorTenantId):
        key "dataTypes": Required[MicrosoftPurviewInformationProtectionConnectorDataTypes]
        key "tenantId": Required[str]
        dataTypes: MicrosoftPurviewInformationProtectionConnectorDataTypes
        tenantId: str


    class azure.mgmt.securityinsight.types.MicrosoftSecurityIncidentCreationAlertRule(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[AlertRuleKind.MICROSOFT_SECURITY_INCIDENT_CREATION]]
        key "name": str
        key "properties": ForwardRef('MicrosoftSecurityIncidentCreationAlertRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[AlertRuleKind.MICROSOFT_SECURITY_INCIDENT_CREATION]
        name: str
        properties: MicrosoftSecurityIncidentCreationAlertRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.MicrosoftSecurityIncidentCreationAlertRuleCommonProperties(TypedDict, total=False):
        key "productFilter": Required[Union[str, MicrosoftSecurityProductName]]
        displayNamesExcludeFilter: list[str]
        displayNamesFilter: list[str]
        productFilter: Union[str, MicrosoftSecurityProductName]
        severitiesFilter: list[Union[str, AlertSeverity]]


    class azure.mgmt.securityinsight.types.MicrosoftSecurityIncidentCreationAlertRuleProperties(MicrosoftSecurityIncidentCreationAlertRuleCommonProperties):
        key "alertRuleTemplateName": str
        key "description": str
        key "displayName": Required[str]
        key "enabled": Required[bool]
        key "lastModifiedUtc": str
        key "productFilter": Required[Union[str, MicrosoftSecurityProductName]]
        alertRuleTemplateName: str
        description: str
        displayName: str
        displayNamesExcludeFilter: list[str]
        displayNamesFilter: list[str]
        enabled: bool
        lastModifiedUtc: str
        productFilter: Union[str, MicrosoftSecurityProductName]
        severitiesFilter: list[Union[str, AlertSeverity]]


    class azure.mgmt.securityinsight.types.MtpCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.MICROSOFT_THREAT_PROTECTION]]
        key "properties": ForwardRef('MTPCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.MICROSOFT_THREAT_PROTECTION]
        properties: MTPCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.MtpFilteredProviders(TypedDict, total=False):
        key "alerts": Required[list[Union[str, MtpProvider]]]
        alerts: list[Union[str, MtpProvider]]


    class azure.mgmt.securityinsight.types.NoneAuthModel(TypedDict, total=False):
        key "type": Required[Literal[CcpAuthType.NONE]]
        type: Literal[CcpAuthType.NONE]


    class azure.mgmt.securityinsight.types.NrtAlertRule(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[AlertRuleKind.NRT]]
        key "name": str
        key "properties": ForwardRef('NrtAlertRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[AlertRuleKind.NRT]
        name: str
        properties: NrtAlertRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.NrtAlertRuleProperties(TypedDict, total=False):
        key "alertDetailsOverride": ForwardRef('AlertDetailsOverride', module='types')
        key "alertRuleTemplateName": str
        key "description": str
        key "displayName": Required[str]
        key "enabled": Required[bool]
        key "eventGroupingSettings": ForwardRef('EventGroupingSettings', module='types')
        key "incidentConfiguration": ForwardRef('IncidentConfiguration', module='types')
        key "lastModifiedUtc": str
        key "query": Required[str]
        key "severity": Required[Union[str, AlertSeverity]]
        key "suppressionDuration": Required[str]
        key "suppressionEnabled": Required[bool]
        key "templateVersion": str
        alertDetailsOverride: AlertDetailsOverride
        alertRuleTemplateName: str
        customDetails: dict[str, str]
        description: str
        displayName: str
        enabled: bool
        entityMappings: list[EntityMapping]
        eventGroupingSettings: EventGroupingSettings
        incidentConfiguration: IncidentConfiguration
        lastModifiedUtc: str
        query: str
        sentinelEntitiesMappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        subTechniques: list[str]
        suppressionDuration: str
        suppressionEnabled: bool
        tactics: list[Union[str, AttackTactic]]
        techniques: list[str]
        templateVersion: str


    class azure.mgmt.securityinsight.types.OAuthModel(TypedDict, total=False):
        key "accessTokenPrepend": str
        key "authorizationCode": str
        key "authorizationEndpoint": str
        key "clientId": Required[str]
        key "clientSecret": Required[str]
        key "grantType": Required[str]
        key "isCredentialsInHeaders": Optional[bool]
        key "isJwtBearerFlow": bool
        key "redirectUri": str
        key "scope": str
        key "tokenEndpoint": Required[str]
        key "type": Required[Literal[CcpAuthType.O_AUTH2]]
        accessTokenPrepend: str
        authorizationCode: str
        authorizationEndpoint: str
        authorizationEndpointHeaders: dict[str, str]
        authorizationEndpointQueryParameters: dict[str, str]
        clientId: str
        clientSecret: str
        grantType: str
        isCredentialsInHeaders: bool
        isJwtBearerFlow: bool
        redirectUri: str
        scope: str
        tokenEndpoint: str
        tokenEndpointHeaders: dict[str, str]
        tokenEndpointQueryParameters: dict[str, str]
        type: Literal[CcpAuthType.O_AUTH2]


    class azure.mgmt.securityinsight.types.Office365ProjectCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.OFFICE365_PROJECT]]
        key "properties": ForwardRef('Office365ProjectCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.OFFICE365_PROJECT]
        properties: Office365ProjectCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.Office365ProjectCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.Office365ProjectConnectorDataTypes(TypedDict, total=False):
        key "logs": Required[Office365ProjectConnectorDataTypesLogs]
        logs: Office365ProjectConnectorDataTypesLogs


    class azure.mgmt.securityinsight.types.Office365ProjectConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.Office365ProjectDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.OFFICE365_PROJECT]]
        key "name": str
        key "properties": ForwardRef('Office365ProjectDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.OFFICE365_PROJECT]
        name: str
        properties: Office365ProjectDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.Office365ProjectDataConnectorProperties(DataConnectorTenantId):
        key "dataTypes": Required[Office365ProjectConnectorDataTypes]
        key "tenantId": Required[str]
        dataTypes: Office365ProjectConnectorDataTypes
        tenantId: str


    class azure.mgmt.securityinsight.types.OfficeATPCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.OFFICE_ATP]]
        key "properties": ForwardRef('OfficeATPCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.OFFICE_ATP]
        properties: OfficeATPCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.OfficeATPCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.OfficeATPDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.OFFICE_ATP]]
        key "name": str
        key "properties": ForwardRef('OfficeATPDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.OFFICE_ATP]
        name: str
        properties: OfficeATPDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.OfficeATPDataConnectorProperties(TypedDict, total=False):
        key "dataTypes": ForwardRef('AlertsDataTypeOfDataConnector', module='types')
        key "tenantId": Required[str]
        dataTypes: AlertsDataTypeOfDataConnector
        tenantId: str


    class azure.mgmt.securityinsight.types.OfficeDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.OFFICE365]]
        key "name": str
        key "properties": ForwardRef('OfficeDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.OFFICE365]
        name: str
        properties: OfficeDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.OfficeDataConnectorDataTypes(TypedDict, total=False):
        key "exchange": Required[OfficeDataConnectorDataTypesExchange]
        key "sharePoint": Required[OfficeDataConnectorDataTypesSharePoint]
        key "teams": Required[OfficeDataConnectorDataTypesTeams]
        exchange: OfficeDataConnectorDataTypesExchange
        sharePoint: OfficeDataConnectorDataTypesSharePoint
        teams: OfficeDataConnectorDataTypesTeams


    class azure.mgmt.securityinsight.types.OfficeDataConnectorDataTypesExchange(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.OfficeDataConnectorDataTypesSharePoint(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.OfficeDataConnectorDataTypesTeams(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.OfficeDataConnectorProperties(DataConnectorTenantId):
        key "dataTypes": Required[OfficeDataConnectorDataTypes]
        key "tenantId": Required[str]
        dataTypes: OfficeDataConnectorDataTypes
        tenantId: str


    class azure.mgmt.securityinsight.types.OfficeIRMCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.OFFICE_IRM]]
        key "properties": ForwardRef('OfficeIRMCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.OFFICE_IRM]
        properties: OfficeIRMCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.OfficeIRMCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.OfficeIRMDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.OFFICE_IRM]]
        key "name": str
        key "properties": ForwardRef('OfficeIRMDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.OFFICE_IRM]
        name: str
        properties: OfficeIRMDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.OfficeIRMDataConnectorProperties(TypedDict, total=False):
        key "dataTypes": ForwardRef('AlertsDataTypeOfDataConnector', module='types')
        key "tenantId": Required[str]
        dataTypes: AlertsDataTypeOfDataConnector
        tenantId: str


    class azure.mgmt.securityinsight.types.OfficePowerBICheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.OFFICE_POWER_BI]]
        key "properties": ForwardRef('OfficePowerBICheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.OFFICE_POWER_BI]
        properties: OfficePowerBICheckRequirementsProperties


    class azure.mgmt.securityinsight.types.OfficePowerBICheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.OfficePowerBIConnectorDataTypes(TypedDict, total=False):
        key "logs": Required[OfficePowerBIConnectorDataTypesLogs]
        logs: OfficePowerBIConnectorDataTypesLogs


    class azure.mgmt.securityinsight.types.OfficePowerBIConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.OfficePowerBIDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.OFFICE_POWER_BI]]
        key "name": str
        key "properties": ForwardRef('OfficePowerBIDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.OFFICE_POWER_BI]
        name: str
        properties: OfficePowerBIDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.OfficePowerBIDataConnectorProperties(DataConnectorTenantId):
        key "dataTypes": Required[OfficePowerBIConnectorDataTypes]
        key "tenantId": Required[str]
        dataTypes: OfficePowerBIConnectorDataTypes
        tenantId: str


    class azure.mgmt.securityinsight.types.OracleAuthModel(TypedDict, total=False):
        key "pemFile": Required[str]
        key "publicFingerprint": Required[str]
        key "tenantId": Required[str]
        key "type": Required[Literal[CcpAuthType.ORACLE]]
        key "userId": Required[str]
        pemFile: str
        publicFingerprint: str
        tenantId: str
        type: Literal[CcpAuthType.ORACLE]
        userId: str


    class azure.mgmt.securityinsight.types.PackageBaseProperties(TypedDict, total=False):
        key "author": ForwardRef('MetadataAuthor', module='types')
        key "categories": ForwardRef('MetadataCategories', module='types')
        key "contentId": str
        key "contentKind": Union[str, PackageKind]
        key "contentProductId": str
        key "contentSchemaVersion": str
        key "dependencies": ForwardRef('MetadataDependencies', module='types')
        key "description": str
        key "displayName": str
        key "firstPublishDate": str
        key "icon": str
        key "isDeprecated": Union[str, Flag]
        key "isFeatured": Union[str, Flag]
        key "isNew": Union[str, Flag]
        key "isPreview": Union[str, Flag]
        key "lastPublishDate": str
        key "publisherDisplayName": str
        key "source": ForwardRef('MetadataSource', module='types')
        key "support": ForwardRef('MetadataSupport', module='types')
        key "version": str
        author: MetadataAuthor
        categories: MetadataCategories
        contentId: str
        contentKind: Union[str, PackageKind]
        contentProductId: str
        contentSchemaVersion: str
        dependencies: MetadataDependencies
        description: str
        displayName: str
        firstPublishDate: str
        icon: str
        isDeprecated: Union[str, Flag]
        isFeatured: Union[str, Flag]
        isNew: Union[str, Flag]
        isPreview: Union[str, Flag]
        lastPublishDate: str
        providers: list[str]
        publisherDisplayName: str
        source: MetadataSource
        support: MetadataSupport
        threatAnalysisTactics: list[str]
        threatAnalysisTechniques: list[str]
        version: str


    class azure.mgmt.securityinsight.types.PackageModel(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('PackageProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: PackageProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.PackageProperties(PackageBaseProperties):
        key "author": ForwardRef('MetadataAuthor', module='types')
        key "categories": ForwardRef('MetadataCategories', module='types')
        key "contentId": str
        key "contentKind": Union[str, PackageKind]
        key "contentProductId": str
        key "contentSchemaVersion": str
        key "dependencies": ForwardRef('MetadataDependencies', module='types')
        key "description": str
        key "displayName": str
        key "firstPublishDate": str
        key "icon": str
        key "isDeprecated": Union[str, Flag]
        key "isFeatured": Union[str, Flag]
        key "isNew": Union[str, Flag]
        key "isPreview": Union[str, Flag]
        key "lastPublishDate": str
        key "publisherDisplayName": str
        key "source": ForwardRef('MetadataSource', module='types')
        key "support": ForwardRef('MetadataSupport', module='types')
        key "version": str
        author: MetadataAuthor
        categories: MetadataCategories
        contentId: str
        contentKind: Union[str, PackageKind]
        contentProductId: str
        contentSchemaVersion: str
        dependencies: MetadataDependencies
        description: str
        displayName: str
        firstPublishDate: str
        icon: str
        isDeprecated: Union[str, Flag]
        isFeatured: Union[str, Flag]
        isNew: Union[str, Flag]
        isPreview: Union[str, Flag]
        lastPublishDate: str
        providers: list[str]
        publisherDisplayName: str
        source: MetadataSource
        support: MetadataSupport
        threatAnalysisTactics: list[str]
        threatAnalysisTechniques: list[str]
        version: str


    class azure.mgmt.securityinsight.types.Permissions(TypedDict, total=False):
        customs: list[PermissionsCustomsItem]
        resourceProvider: list[PermissionsResourceProviderItem]


    class azure.mgmt.securityinsight.types.PermissionsCustomsItem(Customs):
        key "description": str
        key "name": str
        description: str
        name: str


    class azure.mgmt.securityinsight.types.PermissionsResourceProviderItem(ResourceProvider):
        key "permissionsDisplayText": str
        key "provider": Union[str, ProviderName]
        key "providerDisplayName": str
        key "requiredPermissions": ForwardRef('RequiredPermissions', module='types')
        key "scope": Union[str, PermissionProviderScope]
        permissionsDisplayText: str
        provider: Union[str, ProviderName]
        providerDisplayName: str
        requiredPermissions: RequiredPermissions
        scope: Union[str, PermissionProviderScope]


    class azure.mgmt.securityinsight.types.PlaybookActionProperties(TypedDict, total=False):
        key "logicAppResourceId": Required[str]
        key "tenantId": str
        logicAppResourceId: str
        tenantId: str


    class azure.mgmt.securityinsight.types.PremiumMdtiDataConnectorDataTypes(TypedDict, total=False):
        key "connector": Required[PremiumMdtiDataConnectorDataTypesConnector]
        connector: PremiumMdtiDataConnectorDataTypesConnector


    class azure.mgmt.securityinsight.types.PremiumMdtiDataConnectorDataTypesConnector(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.PremiumMdtiDataConnectorProperties(DataConnectorTenantId):
        key "dataTypes": Required[PremiumMdtiDataConnectorDataTypes]
        key "lookbackPeriod": Required[str]
        key "requiredSKUsPresent": bool
        key "tenantId": Required[str]
        dataTypes: PremiumMdtiDataConnectorDataTypes
        lookbackPeriod: str
        requiredSKUsPresent: bool
        tenantId: str


    class azure.mgmt.securityinsight.types.PremiumMicrosoftDefenderForThreatIntelligence(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.PREMIUM_MICROSOFT_DEFENDER_FOR_THREAT_INTELLIGENCE]]
        key "name": str
        key "properties": ForwardRef('PremiumMdtiDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.PREMIUM_MICROSOFT_DEFENDER_FOR_THREAT_INTELLIGENCE]
        name: str
        properties: PremiumMdtiDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.PropertyArrayChangedConditionProperties(TypedDict, total=False):
        key "conditionProperties": ForwardRef('AutomationRulePropertyArrayChangedValuesCondition', module='types')
        key "conditionType": Required[Literal[ConditionType.PROPERTY_ARRAY_CHANGED]]
        conditionProperties: AutomationRulePropertyArrayChangedValuesCondition
        conditionType: Literal[ConditionType.PROPERTY_ARRAY_CHANGED]


    class azure.mgmt.securityinsight.types.PropertyArrayConditionProperties(TypedDict, total=False):
        key "conditionProperties": ForwardRef('AutomationRulePropertyArrayValuesCondition', module='types')
        key "conditionType": Required[Literal[ConditionType.PROPERTY_ARRAY]]
        conditionProperties: AutomationRulePropertyArrayValuesCondition
        conditionType: Literal[ConditionType.PROPERTY_ARRAY]


    class azure.mgmt.securityinsight.types.PropertyChangedConditionProperties(TypedDict, total=False):
        key "conditionProperties": ForwardRef('AutomationRulePropertyValuesChangedCondition', module='types')
        key "conditionType": Required[Literal[ConditionType.PROPERTY_CHANGED]]
        conditionProperties: AutomationRulePropertyValuesChangedCondition
        conditionType: Literal[ConditionType.PROPERTY_CHANGED]


    class azure.mgmt.securityinsight.types.PropertyConditionProperties(TypedDict, total=False):
        key "conditionProperties": ForwardRef('AutomationRulePropertyValuesCondition', module='types')
        key "conditionType": Required[Literal[ConditionType.PROPERTY]]
        conditionProperties: AutomationRulePropertyValuesCondition
        conditionType: Literal[ConditionType.PROPERTY]


    class azure.mgmt.securityinsight.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.PullRequest(TypedDict, total=False):
        key "state": Union[str, PullRequestState]
        key "url": str
        state: Union[str, PullRequestState]
        url: str


    class azure.mgmt.securityinsight.types.PurviewAuditCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.PURVIEW_AUDIT]]
        key "properties": ForwardRef('PurviewAuditCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.PURVIEW_AUDIT]
        properties: PurviewAuditCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.PurviewAuditCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.PurviewAuditConnectorDataTypes(TypedDict, total=False):
        key "logs": Required[PurviewAuditConnectorDataTypesLogs]
        logs: PurviewAuditConnectorDataTypesLogs


    class azure.mgmt.securityinsight.types.PurviewAuditConnectorDataTypesLogs(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.PurviewAuditDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.PURVIEW_AUDIT]]
        key "name": str
        key "properties": ForwardRef('PurviewAuditDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.PURVIEW_AUDIT]
        name: str
        properties: PurviewAuditDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.PurviewAuditDataConnectorProperties(DataConnectorTenantId):
        key "connectorDefinitionName": str
        key "dataTypes": Required[PurviewAuditConnectorDataTypes]
        key "dcrConfig": ForwardRef('DCRConfiguration', module='types')
        key "sourceType": str
        key "tenantId": Required[str]
        connectorDefinitionName: str
        dataTypes: PurviewAuditConnectorDataTypes
        dcrConfig: DCRConfiguration
        sourceType: str
        tenantId: str


    class azure.mgmt.securityinsight.types.Query(TypedDict, total=False):
        key "condition": ForwardRef('QueryCondition', module='types')
        key "maxPageSize": int
        key "minPageSize": int
        key "sortBy": ForwardRef('QuerySortBy', module='types')
        condition: QueryCondition
        maxPageSize: int
        minPageSize: int
        sortBy: QuerySortBy


    class azure.mgmt.securityinsight.types.QueryCondition(TypedDict, total=False):
        key "clauses": Required[list[ConditionClause]]
        key "conditionConnective": Union[str, Connective]
        key "stixObjectType": str
        clauses: list[ConditionClause]
        conditionConnective: Union[str, Connective]
        stixObjectType: str


    class azure.mgmt.securityinsight.types.QueryProperties(TypedDict, total=False):
        key "condition": ForwardRef('ConditionProperties', module='types')
        condition: ConditionProperties


    class azure.mgmt.securityinsight.types.QuerySortBy(TypedDict, total=False):
        key "direction": Union[str, SortingDirection]
        key "field": str
        direction: Union[str, SortingDirection]
        field: str


    class azure.mgmt.securityinsight.types.RecommendationPatch(TypedDict, total=False):
        key "properties": ForwardRef('RecommendationPatchProperties', module='types')
        properties: RecommendationPatchProperties


    class azure.mgmt.securityinsight.types.RecommendationPatchProperties(TypedDict, total=False):
        key "state": Union[str, State]
        state: Union[str, State]


    class azure.mgmt.securityinsight.types.Relation(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('RelationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: RelationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.RelationProperties(TypedDict, total=False):
        key "relatedResourceId": Required[str]
        key "relatedResourceKind": str
        key "relatedResourceName": str
        key "relatedResourceType": str
        relatedResourceId: str
        relatedResourceKind: str
        relatedResourceName: str
        relatedResourceType: str


    class azure.mgmt.securityinsight.types.Repository(TypedDict, total=False):
        key "branch": Required[str]
        key "deploymentLogsUrl": str
        key "displayUrl": str
        key "url": Required[str]
        branch: str
        deploymentLogsUrl: str
        displayUrl: str
        url: str


    class azure.mgmt.securityinsight.types.RepositoryAccess(TypedDict, total=False):
        key "clientId": str
        key "code": str
        key "installationId": str
        key "kind": Required[Union[str, RepositoryAccessKind]]
        key "state": str
        key "token": str
        clientId: str
        code: str
        installationId: str
        kind: Union[str, RepositoryAccessKind]
        state: str
        token: str


    class azure.mgmt.securityinsight.types.RepositoryAccessObject(TypedDict, total=False):
        key "repositoryAccess": Required[RepositoryAccess]
        repositoryAccess: RepositoryAccess


    class azure.mgmt.securityinsight.types.RepositoryAccessProperties(TypedDict, total=False):
        key "properties": Required[RepositoryAccessObject]
        properties: RepositoryAccessObject


    class azure.mgmt.securityinsight.types.RepositoryResourceInfo(TypedDict, total=False):
        key "azureDevOpsResourceInfo": ForwardRef('AzureDevOpsResourceInfo', module='types')
        key "gitHubResourceInfo": ForwardRef('GitHubResourceInfo', module='types')
        key "webhook": ForwardRef('Webhook', module='types')
        azureDevOpsResourceInfo: AzureDevOpsResourceInfo
        gitHubResourceInfo: GitHubResourceInfo
        webhook: Webhook


    class azure.mgmt.securityinsight.types.RequiredPermissions(TypedDict, total=False):
        key "action": bool
        key "delete": bool
        key "read": bool
        key "write": bool
        action: bool
        delete: bool
        read: bool
        write: bool


    class azure.mgmt.securityinsight.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.ResourceProvider(TypedDict, total=False):
        key "permissionsDisplayText": str
        key "provider": Union[str, ProviderName]
        key "providerDisplayName": str
        key "requiredPermissions": ForwardRef('RequiredPermissions', module='types')
        key "scope": Union[str, PermissionProviderScope]
        permissionsDisplayText: str
        provider: Union[str, ProviderName]
        providerDisplayName: str
        requiredPermissions: RequiredPermissions
        scope: Union[str, PermissionProviderScope]


    class azure.mgmt.securityinsight.types.ResourceProviderRequiredPermissions(TypedDict, total=False):
        key "action": bool
        key "delete": bool
        key "read": bool
        key "write": bool
        action: bool
        delete: bool
        read: bool
        write: bool


    class azure.mgmt.securityinsight.types.ResourceWithEtag(Resource):
        key "etag": str
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.RestApiPollerDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.REST_API_POLLER]]
        key "name": str
        key "properties": ForwardRef('RestApiPollerDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.REST_API_POLLER]
        name: str
        properties: RestApiPollerDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.RestApiPollerDataConnectorProperties(TypedDict, total=False):
        key "auth": Required[CcpAuthConfig]
        key "connectorDefinitionName": Required[str]
        key "dataType": str
        key "dcrConfig": ForwardRef('DCRConfiguration', module='types')
        key "isActive": bool
        key "paging": ForwardRef('RestApiPollerRequestPagingConfig', module='types')
        key "request": Required[RestApiPollerRequestConfig]
        key "response": ForwardRef('CcpResponseConfig', module='types')
        addOnAttributes: dict[str, str]
        auth: CcpAuthConfig
        connectorDefinitionName: str
        dataType: str
        dcrConfig: DCRConfiguration
        isActive: bool
        paging: RestApiPollerRequestPagingConfig
        request: RestApiPollerRequestConfig
        response: CcpResponseConfig


    class azure.mgmt.securityinsight.types.RestApiPollerRequestConfig(TypedDict, total=False):
        key "apiEndpoint": Required[str]
        key "endTimeAttributeName": str
        key "httpMethod": Union[str, HttpMethodVerb]
        key "isPostPayloadJson": Optional[bool]
        key "queryParametersTemplate": str
        key "queryTimeFormat": str
        key "queryTimeIntervalAttributeName": str
        key "queryTimeIntervalDelimiter": str
        key "queryTimeIntervalPrepend": str
        key "queryWindowInMin": Optional[int]
        key "rateLimitQPS": Optional[int]
        key "retryCount": Optional[int]
        key "startTimeAttributeName": str
        key "timeoutInSeconds": Optional[int]
        apiEndpoint: str
        endTimeAttributeName: str
        headers: dict[str, str]
        httpMethod: Union[str, HttpMethodVerb]
        isPostPayloadJson: bool
        queryParameters: dict[str, Any]
        queryParametersTemplate: str
        queryTimeFormat: str
        queryTimeIntervalAttributeName: str
        queryTimeIntervalDelimiter: str
        queryTimeIntervalPrepend: str
        queryWindowInMin: int
        rateLimitQPS: int
        retryCount: int
        startTimeAttributeName: str
        timeoutInSeconds: int


    class azure.mgmt.securityinsight.types.RestApiPollerRequestPagingConfig(TypedDict, total=False):
        key "pageSize": int
        key "pageSizeParameterName": str
        key "pagingType": Required[Union[str, RestApiPollerRequestPagingKind]]
        pageSize: int
        pageSizeParameterName: str
        pagingType: Union[str, RestApiPollerRequestPagingKind]


    class azure.mgmt.securityinsight.types.SampleQueries(TypedDict, total=False):
        key "description": str
        key "query": str
        description: str
        query: str


    class azure.mgmt.securityinsight.types.ScheduledAlertRule(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[AlertRuleKind.SCHEDULED]]
        key "name": str
        key "properties": ForwardRef('ScheduledAlertRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[AlertRuleKind.SCHEDULED]
        name: str
        properties: ScheduledAlertRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.ScheduledAlertRuleCommonProperties(TypedDict, total=False):
        key "alertDetailsOverride": ForwardRef('AlertDetailsOverride', module='types')
        key "eventGroupingSettings": ForwardRef('EventGroupingSettings', module='types')
        key "query": str
        key "queryFrequency": str
        key "queryPeriod": str
        key "severity": Union[str, AlertSeverity]
        key "triggerOperator": Union[str, TriggerOperator]
        key "triggerThreshold": int
        alertDetailsOverride: AlertDetailsOverride
        customDetails: dict[str, str]
        entityMappings: list[EntityMapping]
        eventGroupingSettings: EventGroupingSettings
        query: str
        queryFrequency: str
        queryPeriod: str
        sentinelEntitiesMappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        triggerOperator: Union[str, TriggerOperator]
        triggerThreshold: int


    class azure.mgmt.securityinsight.types.ScheduledAlertRuleProperties(ScheduledAlertRuleCommonProperties):
        key "alertDetailsOverride": ForwardRef('AlertDetailsOverride', module='types')
        key "alertRuleTemplateName": str
        key "description": str
        key "displayName": Required[str]
        key "enabled": Required[bool]
        key "eventGroupingSettings": ForwardRef('EventGroupingSettings', module='types')
        key "incidentConfiguration": ForwardRef('IncidentConfiguration', module='types')
        key "lastModifiedUtc": str
        key "query": str
        key "queryFrequency": str
        key "queryPeriod": str
        key "severity": Union[str, AlertSeverity]
        key "suppressionDuration": Required[str]
        key "suppressionEnabled": Required[bool]
        key "templateVersion": str
        key "triggerOperator": Union[str, TriggerOperator]
        key "triggerThreshold": int
        alertDetailsOverride: AlertDetailsOverride
        alertRuleTemplateName: str
        customDetails: dict[str, str]
        description: str
        displayName: str
        enabled: bool
        entityMappings: list[EntityMapping]
        eventGroupingSettings: EventGroupingSettings
        incidentConfiguration: IncidentConfiguration
        lastModifiedUtc: str
        query: str
        queryFrequency: str
        queryPeriod: str
        sentinelEntitiesMappings: list[SentinelEntityMapping]
        severity: Union[str, AlertSeverity]
        subTechniques: list[str]
        suppressionDuration: str
        suppressionEnabled: bool
        tactics: list[Union[str, AttackTactic]]
        techniques: list[str]
        templateVersion: str
        triggerOperator: Union[str, TriggerOperator]
        triggerThreshold: int


    class azure.mgmt.securityinsight.types.SecurityMLAnalyticsSetting(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[SecurityMLAnalyticsSettingsKind.ANOMALY]]
        key "name": str
        key "properties": ForwardRef('AnomalySecurityMLAnalyticsSettingsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[SecurityMLAnalyticsSettingsKind.ANOMALY]
        name: str
        properties: AnomalySecurityMLAnalyticsSettingsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.SecurityMLAnalyticsSettingsDataSource(TypedDict, total=False):
        key "connectorId": str
        connectorId: str
        dataTypes: list[str]


    class azure.mgmt.securityinsight.types.SecurityMLAnalyticsSettingsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANOMALY = "Anomaly"


    class azure.mgmt.securityinsight.types.SentinelEntityMapping(TypedDict, total=False):
        key "columnName": str
        columnName: str


    class azure.mgmt.securityinsight.types.SentinelOnboardingState(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('SentinelOnboardingStateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: SentinelOnboardingStateProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.SentinelOnboardingStateProperties(TypedDict, total=False):
        key "customerManagedKey": bool
        customerManagedKey: bool


    class azure.mgmt.securityinsight.types.ServicePrincipal(TypedDict, total=False):
        key "appId": str
        key "credentialsExpireOn": str
        key "id": str
        key "tenantId": str
        appId: str
        credentialsExpireOn: str
        id: str
        tenantId: str


    class azure.mgmt.securityinsight.types.SessionAuthModel(TypedDict, total=False):
        key "isPostPayloadJson": Optional[bool]
        key "password": Required[dict[str, str]]
        key "sessionIdName": str
        key "sessionLoginRequestUri": str
        key "sessionTimeoutInMinutes": Optional[int]
        key "type": Required[Literal[CcpAuthType.SESSION]]
        key "userName": Required[dict[str, str]]
        headers: dict[str, str]
        isPostPayloadJson: bool
        password: dict[str, str]
        queryParameters: dict[str, Any]
        sessionIdName: str
        sessionLoginRequestUri: str
        sessionTimeoutInMinutes: int
        type: Literal[CcpAuthType.SESSION]
        userName: dict[str, str]


    class azure.mgmt.securityinsight.types.SettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANOMALIES = "Anomalies"
        ENTITY_ANALYTICS = "EntityAnalytics"
        EYES_ON = "EyesOn"
        UEBA = "Ueba"


    class azure.mgmt.securityinsight.types.SourceControl(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": Required[SourceControlProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: SourceControlProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.SourceControlProperties(TypedDict, total=False):
        key "contentTypes": Required[list[Union[str, ContentType]]]
        key "description": str
        key "displayName": Required[str]
        key "id": str
        key "lastDeploymentInfo": ForwardRef('DeploymentInfo', module='types')
        key "pullRequest": ForwardRef('PullRequest', module='types')
        key "repoType": Required[Union[str, RepoType]]
        key "repository": Required[Repository]
        key "repositoryAccess": ForwardRef('RepositoryAccess', module='types')
        key "repositoryResourceInfo": ForwardRef('RepositoryResourceInfo', module='types')
        key "servicePrincipal": ForwardRef('ServicePrincipal', module='types')
        key "version": Union[str, Version]
        key "workloadIdentityFederation": ForwardRef('WorkloadIdentityFederation', module='types')
        contentTypes: list[Union[str, ContentType]]
        description: str
        displayName: str
        id: str
        lastDeploymentInfo: DeploymentInfo
        pullRequest: PullRequest
        repoType: Union[str, RepoType]
        repository: Repository
        repositoryAccess: RepositoryAccess
        repositoryResourceInfo: RepositoryResourceInfo
        servicePrincipal: ServicePrincipal
        version: Union[str, Version]
        workloadIdentityFederation: WorkloadIdentityFederation


    class azure.mgmt.securityinsight.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.securityinsight.types.TICheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.THREAT_INTELLIGENCE]]
        key "properties": ForwardRef('TICheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.THREAT_INTELLIGENCE]
        properties: TICheckRequirementsProperties


    class azure.mgmt.securityinsight.types.TICheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.TIDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.THREAT_INTELLIGENCE]]
        key "name": str
        key "properties": ForwardRef('TIDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.THREAT_INTELLIGENCE]
        name: str
        properties: TIDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.TIDataConnectorDataTypes(TypedDict, total=False):
        key "indicators": Required[TIDataConnectorDataTypesIndicators]
        indicators: TIDataConnectorDataTypesIndicators


    class azure.mgmt.securityinsight.types.TIDataConnectorDataTypesIndicators(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.TIDataConnectorProperties(DataConnectorTenantId):
        key "dataTypes": Required[TIDataConnectorDataTypes]
        key "tenantId": Required[str]
        key "tipLookbackPeriod": Optional[str]
        dataTypes: TIDataConnectorDataTypes
        tenantId: str
        tipLookbackPeriod: str


    class azure.mgmt.securityinsight.types.TeamInformation(TypedDict, total=False):
        key "description": str
        key "name": str
        key "primaryChannelUrl": str
        key "teamCreationTimeUtc": str
        key "teamId": str
        description: str
        name: str
        primaryChannelUrl: str
        teamCreationTimeUtc: str
        teamId: str


    class azure.mgmt.securityinsight.types.TemplateModel(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('TemplateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: TemplateProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.TemplateProperties(TypedDict, total=False):
        key "author": ForwardRef('MetadataAuthor', module='types')
        key "categories": ForwardRef('MetadataCategories', module='types')
        key "contentId": str
        key "contentKind": Union[str, Kind]
        key "contentProductId": str
        key "contentSchemaVersion": str
        key "customVersion": str
        key "dependencies": ForwardRef('MetadataDependencies', module='types')
        key "displayName": str
        key "firstPublishDate": str
        key "icon": str
        key "isDeprecated": Union[str, Flag]
        key "lastPublishDate": str
        key "mainTemplate": Any
        key "packageId": str
        key "packageKind": Union[str, PackageKind]
        key "packageName": str
        key "packageVersion": str
        key "source": ForwardRef('MetadataSource', module='types')
        key "support": ForwardRef('MetadataSupport', module='types')
        key "version": str
        author: MetadataAuthor
        categories: MetadataCategories
        contentId: str
        contentKind: Union[str, Kind]
        contentProductId: str
        contentSchemaVersion: str
        customVersion: str
        dependantTemplates: list[TemplateProperties]
        dependencies: MetadataDependencies
        displayName: str
        firstPublishDate: str
        icon: str
        isDeprecated: Union[str, Flag]
        lastPublishDate: str
        mainTemplate: Any
        packageId: str
        packageKind: Union[str, PackageKind]
        packageName: str
        packageVersion: str
        previewImages: list[str]
        previewImagesDark: list[str]
        providers: list[str]
        source: MetadataSource
        support: MetadataSupport
        threatAnalysisTactics: list[str]
        threatAnalysisTechniques: list[str]
        version: str


    class azure.mgmt.securityinsight.types.ThreatIntelligenceAlertRule(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[AlertRuleKind.THREAT_INTELLIGENCE]]
        key "name": str
        key "properties": ForwardRef('ThreatIntelligenceAlertRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[AlertRuleKind.THREAT_INTELLIGENCE]
        name: str
        properties: ThreatIntelligenceAlertRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.ThreatIntelligenceAlertRuleProperties(TypedDict, total=False):
        key "alertRuleTemplateName": Required[str]
        key "description": str
        key "displayName": str
        key "enabled": Required[bool]
        key "lastModifiedUtc": str
        key "severity": Union[str, AlertSeverity]
        alertRuleTemplateName: str
        description: str
        displayName: str
        enabled: bool
        lastModifiedUtc: str
        severity: Union[str, AlertSeverity]
        subTechniques: list[str]
        tactics: list[Union[str, AttackTactic]]
        techniques: list[str]


    class azure.mgmt.securityinsight.types.ThreatIntelligenceAppendTags(TypedDict, total=False):
        threatIntelligenceTags: list[str]


    class azure.mgmt.securityinsight.types.ThreatIntelligenceExternalReference(TypedDict, total=False):
        key "description": str
        key "externalId": str
        key "sourceName": str
        key "url": str
        description: str
        externalId: str
        hashes: dict[str, str]
        sourceName: str
        url: str


    class azure.mgmt.securityinsight.types.ThreatIntelligenceFilteringCriteria(TypedDict, total=False):
        key "includeDisabled": bool
        key "maxConfidence": int
        key "maxValidUntil": str
        key "minConfidence": int
        key "minValidUntil": str
        key "pageSize": int
        key "skipToken": str
        ids: list[str]
        includeDisabled: bool
        keywords: list[str]
        maxConfidence: int
        maxValidUntil: str
        minConfidence: int
        minValidUntil: str
        pageSize: int
        patternTypes: list[str]
        skipToken: str
        sortBy: list[ThreatIntelligenceSortingCriteria]
        sources: list[str]
        threatTypes: list[str]


    class azure.mgmt.securityinsight.types.ThreatIntelligenceGranularMarkingModel(TypedDict, total=False):
        key "language": str
        key "markingRef": int
        language: str
        markingRef: int
        selectors: list[str]


    class azure.mgmt.securityinsight.types.ThreatIntelligenceIndicatorModel(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[ThreatIntelligenceResourceKindEnum.INDICATOR]]
        key "name": str
        key "properties": ForwardRef('ThreatIntelligenceIndicatorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[ThreatIntelligenceResourceKindEnum.INDICATOR]
        name: str
        properties: ThreatIntelligenceIndicatorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.ThreatIntelligenceIndicatorProperties(EntityCommonProperties):
        key "confidence": int
        key "created": str
        key "createdByRef": str
        key "defanged": bool
        key "description": str
        key "displayName": str
        key "externalId": str
        key "externalLastUpdatedTimeUtc": str
        key "friendlyName": str
        key "language": str
        key "lastUpdatedTimeUtc": str
        key "modified": str
        key "pattern": str
        key "patternType": str
        key "patternVersion": str
        key "revoked": bool
        key "source": str
        key "validFrom": str
        key "validUntil": str
        additionalData: dict[str, Any]
        confidence: int
        created: str
        createdByRef: str
        defanged: bool
        description: str
        displayName: str
        extensions: dict[str, Any]
        externalId: str
        externalLastUpdatedTimeUtc: str
        externalReferences: list[ThreatIntelligenceExternalReference]
        friendlyName: str
        granularMarkings: list[ThreatIntelligenceGranularMarkingModel]
        indicatorTypes: list[str]
        killChainPhases: list[ThreatIntelligenceKillChainPhase]
        labels: list[str]
        language: str
        lastUpdatedTimeUtc: str
        modified: str
        objectMarkingRefs: list[str]
        parsedPattern: list[ThreatIntelligenceParsedPattern]
        pattern: str
        patternType: str
        patternVersion: str
        revoked: bool
        source: str
        threatIntelligenceTags: list[str]
        threatTypes: list[str]
        validFrom: str
        validUntil: str


    class azure.mgmt.securityinsight.types.ThreatIntelligenceInformation(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[ThreatIntelligenceResourceKindEnum.INDICATOR]]
        key "name": str
        key "properties": ForwardRef('ThreatIntelligenceIndicatorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[ThreatIntelligenceResourceKindEnum.INDICATOR]
        name: str
        properties: ThreatIntelligenceIndicatorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.ThreatIntelligenceKillChainPhase(TypedDict, total=False):
        key "killChainName": str
        key "phaseName": str
        killChainName: str
        phaseName: str


    class azure.mgmt.securityinsight.types.ThreatIntelligenceParsedPattern(TypedDict, total=False):
        key "patternTypeKey": str
        patternTypeKey: str
        patternTypeValues: list[ThreatIntelligenceParsedPatternTypeValue]


    class azure.mgmt.securityinsight.types.ThreatIntelligenceParsedPatternTypeValue(TypedDict, total=False):
        key "value": str
        key "valueType": str
        value: str
        valueType: str


    class azure.mgmt.securityinsight.types.ThreatIntelligenceResourceKindEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INDICATOR = "indicator"


    class azure.mgmt.securityinsight.types.ThreatIntelligenceSortingCriteria(TypedDict, total=False):
        key "itemKey": str
        key "sortOrder": Union[str, ThreatIntelligenceSortingCriteriaEnum]
        itemKey: str
        sortOrder: Union[str, ThreatIntelligenceSortingCriteriaEnum]


    class azure.mgmt.securityinsight.types.TiTaxiiCheckRequirements(TypedDict, total=False):
        key "kind": Required[Literal[DataConnectorKind.THREAT_INTELLIGENCE_TAXII]]
        key "properties": ForwardRef('TiTaxiiCheckRequirementsProperties', module='types')
        kind: Literal[DataConnectorKind.THREAT_INTELLIGENCE_TAXII]
        properties: TiTaxiiCheckRequirementsProperties


    class azure.mgmt.securityinsight.types.TiTaxiiCheckRequirementsProperties(DataConnectorTenantId):
        key "tenantId": Required[str]
        tenantId: str


    class azure.mgmt.securityinsight.types.TiTaxiiDataConnector(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[DataConnectorKind.THREAT_INTELLIGENCE_TAXII]]
        key "name": str
        key "properties": ForwardRef('TiTaxiiDataConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[DataConnectorKind.THREAT_INTELLIGENCE_TAXII]
        name: str
        properties: TiTaxiiDataConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.TiTaxiiDataConnectorDataTypes(TypedDict, total=False):
        key "taxiiClient": Required[TiTaxiiDataConnectorDataTypesTaxiiClient]
        taxiiClient: TiTaxiiDataConnectorDataTypesTaxiiClient


    class azure.mgmt.securityinsight.types.TiTaxiiDataConnectorDataTypesTaxiiClient(DataConnectorDataTypeCommon):
        key "state": Required[Union[str, DataTypeState]]
        state: Union[str, DataTypeState]


    class azure.mgmt.securityinsight.types.TiTaxiiDataConnectorProperties(DataConnectorTenantId):
        key "collectionId": str
        key "dataTypes": Required[TiTaxiiDataConnectorDataTypes]
        key "friendlyName": str
        key "password": str
        key "pollingFrequency": Required[Optional[Union[str, PollingFrequency]]]
        key "taxiiLookbackPeriod": Optional[str]
        key "taxiiServer": str
        key "tenantId": Required[str]
        key "userName": str
        key "workspaceId": str
        collectionId: str
        dataTypes: TiTaxiiDataConnectorDataTypes
        friendlyName: str
        password: str
        pollingFrequency: Union[str, PollingFrequency]
        taxiiLookbackPeriod: str
        taxiiServer: str
        tenantId: str
        userName: str
        workspaceId: str


    class azure.mgmt.securityinsight.types.Ueba(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "kind": Required[Literal[SettingKind.UEBA]]
        key "name": str
        key "properties": ForwardRef('UebaProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: Literal[SettingKind.UEBA]
        name: str
        properties: UebaProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.UebaProperties(TypedDict, total=False):
        dataSources: list[Union[str, UebaDataSources]]


    class azure.mgmt.securityinsight.types.UserInfo(TypedDict, total=False):
        key "email": str
        key "name": str
        key "objectId": Optional[str]
        email: str
        name: str
        objectId: str


    class azure.mgmt.securityinsight.types.ValidationError(TypedDict, total=False):
        key "recordIndex": int
        errorMessages: list[str]
        recordIndex: int


    class azure.mgmt.securityinsight.types.Watchlist(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('WatchlistProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: WatchlistProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.WatchlistItem(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('WatchlistItemProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: WatchlistItemProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.WatchlistItemProperties(TypedDict, total=False):
        key "created": str
        key "createdBy": ForwardRef('UserInfo', module='types')
        key "entityMapping": Any
        key "isDeleted": bool
        key "itemsKeyValue": Required[Any]
        key "tenantId": str
        key "updated": str
        key "updatedBy": ForwardRef('UserInfo', module='types')
        key "watchlistItemId": str
        key "watchlistItemType": str
        created: str
        createdBy: UserInfo
        entityMapping: Any
        isDeleted: bool
        itemsKeyValue: Any
        tenantId: str
        updated: str
        updatedBy: UserInfo
        watchlistItemId: str
        watchlistItemType: str


    class azure.mgmt.securityinsight.types.WatchlistProperties(TypedDict, total=False):
        key "contentType": str
        key "created": str
        key "createdBy": ForwardRef('UserInfo', module='types')
        key "defaultDuration": str
        key "description": str
        key "displayName": Required[str]
        key "isDeleted": bool
        key "itemsSearchKey": Required[str]
        key "numberOfLinesToSkip": int
        key "provider": Required[str]
        key "provisioningState": Union[str, WatchlistProvisioningState]
        key "rawContent": str
        key "source": str
        key "sourceType": Union[str, SourceType]
        key "tenantId": str
        key "updated": str
        key "updatedBy": ForwardRef('UserInfo', module='types')
        key "uploadStatus": str
        key "watchlistAlias": str
        key "watchlistId": str
        key "watchlistType": str
        contentType: str
        created: str
        createdBy: UserInfo
        defaultDuration: str
        description: str
        displayName: str
        isDeleted: bool
        itemsSearchKey: str
        labels: list[str]
        numberOfLinesToSkip: int
        provider: str
        provisioningState: Union[str, WatchlistProvisioningState]
        rawContent: str
        source: str
        sourceType: Union[str, SourceType]
        tenantId: str
        updated: str
        updatedBy: UserInfo
        uploadStatus: str
        watchlistAlias: str
        watchlistId: str
        watchlistType: str


    class azure.mgmt.securityinsight.types.Webhook(TypedDict, total=False):
        key "rotateWebhookSecret": bool
        key "webhookId": str
        key "webhookSecretUpdateTime": str
        key "webhookUrl": str
        rotateWebhookSecret: bool
        webhookId: str
        webhookSecretUpdateTime: str
        webhookUrl: str


    class azure.mgmt.securityinsight.types.WorkloadIdentityFederation(TypedDict, total=False):
        key "appId": str
        key "id": str
        key "issuer": str
        key "subject": str
        key "tenantId": str
        appId: str
        id: str
        issuer: str
        subject: str
        tenantId: str


    class azure.mgmt.securityinsight.types.WorkspaceManagerAssignment(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('WorkspaceManagerAssignmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: WorkspaceManagerAssignmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.WorkspaceManagerAssignmentProperties(TypedDict, total=False):
        key "items": Required[list[AssignmentItem]]
        key "lastJobEndTime": str
        key "lastJobProvisioningState": Union[str, JobProvisioningState]
        key "targetResourceName": Required[str]
        items: list[AssignmentItem]
        lastJobEndTime: str
        lastJobProvisioningState: Union[str, JobProvisioningState]
        targetResourceName: str


    class azure.mgmt.securityinsight.types.WorkspaceManagerConfiguration(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('WorkspaceManagerConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: WorkspaceManagerConfigurationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.WorkspaceManagerConfigurationProperties(TypedDict, total=False):
        key "mode": Required[Union[str, Mode]]
        mode: Union[str, Mode]


    class azure.mgmt.securityinsight.types.WorkspaceManagerGroup(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('WorkspaceManagerGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: WorkspaceManagerGroupProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.WorkspaceManagerGroupProperties(TypedDict, total=False):
        key "description": str
        key "displayName": Required[str]
        key "memberResourceNames": Required[list[str]]
        description: str
        displayName: str
        memberResourceNames: list[str]


    class azure.mgmt.securityinsight.types.WorkspaceManagerMember(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('WorkspaceManagerMemberProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: WorkspaceManagerMemberProperties
        systemData: SystemData
        type: str


    class azure.mgmt.securityinsight.types.WorkspaceManagerMemberProperties(TypedDict, total=False):
        key "targetWorkspaceResourceId": Required[str]
        key "targetWorkspaceTenantId": Required[str]
        targetWorkspaceResourceId: str
        targetWorkspaceTenantId: str


```