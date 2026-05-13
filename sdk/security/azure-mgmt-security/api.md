```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.security

    class azure.mgmt.security.SecurityCenter: implements ContextManager 
        advanced_threat_protection: AdvancedThreatProtectionOperations
        alerts: AlertsOperations
        alerts_suppression_rules: AlertsSuppressionRulesOperations
        allowed_connections: AllowedConnectionsOperations
        api_collections: APICollectionsOperations
        application: ApplicationOperations
        applications: ApplicationsOperations
        assessments: AssessmentsOperations
        assessments_metadata: AssessmentsMetadataOperations
        auto_provisioning_settings: AutoProvisioningSettingsOperations
        automations: AutomationsOperations
        azure_dev_ops_orgs: AzureDevOpsOrgsOperations
        azure_dev_ops_projects: AzureDevOpsProjectsOperations
        azure_dev_ops_repos: AzureDevOpsReposOperations
        compliance_results: ComplianceResultsOperations
        compliances: CompliancesOperations
        connectors: ConnectorsOperations
        custom_assessment_automations: CustomAssessmentAutomationsOperations
        custom_entity_store_assignments: CustomEntityStoreAssignmentsOperations
        custom_recommendations: CustomRecommendationsOperations
        defender_for_storage: DefenderForStorageOperations
        dev_ops_configurations: DevOpsConfigurationsOperations
        dev_ops_operation_results: DevOpsOperationResultsOperations
        device_security_groups: DeviceSecurityGroupsOperations
        discovered_security_solutions: DiscoveredSecuritySolutionsOperations
        external_security_solutions: ExternalSecuritySolutionsOperations
        git_hub_owners: GitHubOwnersOperations
        git_hub_repos: GitHubReposOperations
        git_lab_groups: GitLabGroupsOperations
        git_lab_projects: GitLabProjectsOperations
        git_lab_subgroups: GitLabSubgroupsOperations
        governance_assignments: GovernanceAssignmentsOperations
        governance_rules: GovernanceRulesOperations
        health_reports: HealthReportsOperations
        information_protection_policies: InformationProtectionPoliciesOperations
        iot_security_solution: IotSecuritySolutionOperations
        iot_security_solution_analytics: IotSecuritySolutionAnalyticsOperations
        iot_security_solutions_analytics_aggregated_alert: IotSecuritySolutionsAnalyticsAggregatedAlertOperations
        iot_security_solutions_analytics_recommendation: IotSecuritySolutionsAnalyticsRecommendationOperations
        jit_network_access_policies: JitNetworkAccessPoliciesOperations
        locations: LocationsOperations
        mde_onboardings: MdeOnboardingsOperations
        operations: Operations
        pricings: PricingsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        private_links: PrivateLinksOperations
        regulatory_compliance_assessments: RegulatoryComplianceAssessmentsOperations
        regulatory_compliance_controls: RegulatoryComplianceControlsOperations
        regulatory_compliance_standards: RegulatoryComplianceStandardsOperations
        secure_score_control_definitions: SecureScoreControlDefinitionsOperations
        secure_score_controls: SecureScoreControlsOperations
        secure_scores: SecureScoresOperations
        security_connector_application: SecurityConnectorApplicationOperations
        security_connector_applications: SecurityConnectorApplicationsOperations
        security_connectors: SecurityConnectorsOperations
        security_contacts: SecurityContactsOperations
        security_operators: SecurityOperatorsOperations
        security_solutions: SecuritySolutionsOperations
        security_solutions_reference_data: SecuritySolutionsReferenceDataOperations
        security_standards: SecurityStandardsOperations
        sensitivity_settings: SensitivitySettingsOperations
        server_vulnerability_assessment: ServerVulnerabilityAssessmentOperations
        server_vulnerability_assessments_settings: ServerVulnerabilityAssessmentsSettingsOperations
        settings: SettingsOperations
        software_inventories: SoftwareInventoriesOperations
        sql_vulnerability_assessment_baseline_rules: SqlVulnerabilityAssessmentBaselineRulesOperations
        sql_vulnerability_assessment_scan_results: SqlVulnerabilityAssessmentScanResultsOperations
        sql_vulnerability_assessment_scans: SqlVulnerabilityAssessmentScansOperations
        standard_assignments: StandardAssignmentsOperations
        sub_assessments: SubAssessmentsOperations
        tasks: TasksOperations
        topology: TopologyOperations
        workspace_settings: WorkspaceSettingsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.security.aio

    class azure.mgmt.security.aio.SecurityCenter: implements AsyncContextManager 
        advanced_threat_protection: AdvancedThreatProtectionOperations
        alerts: AlertsOperations
        alerts_suppression_rules: AlertsSuppressionRulesOperations
        allowed_connections: AllowedConnectionsOperations
        api_collections: APICollectionsOperations
        application: ApplicationOperations
        applications: ApplicationsOperations
        assessments: AssessmentsOperations
        assessments_metadata: AssessmentsMetadataOperations
        auto_provisioning_settings: AutoProvisioningSettingsOperations
        automations: AutomationsOperations
        azure_dev_ops_orgs: AzureDevOpsOrgsOperations
        azure_dev_ops_projects: AzureDevOpsProjectsOperations
        azure_dev_ops_repos: AzureDevOpsReposOperations
        compliance_results: ComplianceResultsOperations
        compliances: CompliancesOperations
        connectors: ConnectorsOperations
        custom_assessment_automations: CustomAssessmentAutomationsOperations
        custom_entity_store_assignments: CustomEntityStoreAssignmentsOperations
        custom_recommendations: CustomRecommendationsOperations
        defender_for_storage: DefenderForStorageOperations
        dev_ops_configurations: DevOpsConfigurationsOperations
        dev_ops_operation_results: DevOpsOperationResultsOperations
        device_security_groups: DeviceSecurityGroupsOperations
        discovered_security_solutions: DiscoveredSecuritySolutionsOperations
        external_security_solutions: ExternalSecuritySolutionsOperations
        git_hub_owners: GitHubOwnersOperations
        git_hub_repos: GitHubReposOperations
        git_lab_groups: GitLabGroupsOperations
        git_lab_projects: GitLabProjectsOperations
        git_lab_subgroups: GitLabSubgroupsOperations
        governance_assignments: GovernanceAssignmentsOperations
        governance_rules: GovernanceRulesOperations
        health_reports: HealthReportsOperations
        information_protection_policies: InformationProtectionPoliciesOperations
        iot_security_solution: IotSecuritySolutionOperations
        iot_security_solution_analytics: IotSecuritySolutionAnalyticsOperations
        iot_security_solutions_analytics_aggregated_alert: IotSecuritySolutionsAnalyticsAggregatedAlertOperations
        iot_security_solutions_analytics_recommendation: IotSecuritySolutionsAnalyticsRecommendationOperations
        jit_network_access_policies: JitNetworkAccessPoliciesOperations
        locations: LocationsOperations
        mde_onboardings: MdeOnboardingsOperations
        operations: Operations
        pricings: PricingsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        private_links: PrivateLinksOperations
        regulatory_compliance_assessments: RegulatoryComplianceAssessmentsOperations
        regulatory_compliance_controls: RegulatoryComplianceControlsOperations
        regulatory_compliance_standards: RegulatoryComplianceStandardsOperations
        secure_score_control_definitions: SecureScoreControlDefinitionsOperations
        secure_score_controls: SecureScoreControlsOperations
        secure_scores: SecureScoresOperations
        security_connector_application: SecurityConnectorApplicationOperations
        security_connector_applications: SecurityConnectorApplicationsOperations
        security_connectors: SecurityConnectorsOperations
        security_contacts: SecurityContactsOperations
        security_operators: SecurityOperatorsOperations
        security_solutions: SecuritySolutionsOperations
        security_solutions_reference_data: SecuritySolutionsReferenceDataOperations
        security_standards: SecurityStandardsOperations
        sensitivity_settings: SensitivitySettingsOperations
        server_vulnerability_assessment: ServerVulnerabilityAssessmentOperations
        server_vulnerability_assessments_settings: ServerVulnerabilityAssessmentsSettingsOperations
        settings: SettingsOperations
        software_inventories: SoftwareInventoriesOperations
        sql_vulnerability_assessment_baseline_rules: SqlVulnerabilityAssessmentBaselineRulesOperations
        sql_vulnerability_assessment_scan_results: SqlVulnerabilityAssessmentScanResultsOperations
        sql_vulnerability_assessment_scans: SqlVulnerabilityAssessmentScansOperations
        standard_assignments: StandardAssignmentsOperations
        sub_assessments: SubAssessmentsOperations
        tasks: TasksOperations
        topology: TopologyOperations
        workspace_settings: WorkspaceSettingsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.security.aio.operations

    class azure.mgmt.security.aio.operations.APICollectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_onboard_azure_api_management_api(
                self, 
                resource_group_name: str, 
                service_name: str, 
                api_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ApiCollection]: ...

        @distributed_trace_async
        async def get_by_azure_api_management_service(
                self, 
                resource_group_name: str, 
                service_name: str, 
                api_id: str, 
                **kwargs: Any
            ) -> ApiCollection: ...

        @distributed_trace
        def list_by_azure_api_management_service(
                self, 
                resource_group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApiCollection]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApiCollection]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ApiCollection]: ...

        @distributed_trace_async
        async def offboard_azure_api_management_api(
                self, 
                resource_group_name: str, 
                service_name: str, 
                api_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.security.aio.operations.AdvancedThreatProtectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_id: str, 
                advanced_threat_protection_setting: AdvancedThreatProtectionSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdvancedThreatProtectionSetting: ...

        @overload
        async def create(
                self, 
                resource_id: str, 
                advanced_threat_protection_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdvancedThreatProtectionSetting: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> AdvancedThreatProtectionSetting: ...


    class azure.mgmt.security.aio.operations.AlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_simulate(
                self, 
                asc_location: str, 
                alert_simulator_request_body: AlertSimulatorRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_simulate(
                self, 
                asc_location: str, 
                alert_simulator_request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_resource_group_level(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace_async
        async def get_subscription_level(
                self, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Alert]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Alert]: ...

        @distributed_trace
        def list_resource_group_level_by_region(
                self, 
                asc_location: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Alert]: ...

        @distributed_trace
        def list_subscription_level_by_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Alert]: ...

        @distributed_trace_async
        async def update_resource_group_level_state_to_activate(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_resource_group_level_state_to_dismiss(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_resource_group_level_state_to_in_progress(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_resource_group_level_state_to_resolve(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_subscription_level_state_to_activate(
                self, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_subscription_level_state_to_dismiss(
                self, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_subscription_level_state_to_in_progress(
                self, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_subscription_level_state_to_resolve(
                self, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.security.aio.operations.AlertsSuppressionRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                alerts_suppression_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                alerts_suppression_rule_name: str, 
                **kwargs: Any
            ) -> AlertsSuppressionRule: ...

        @distributed_trace
        def list(
                self, 
                alert_type: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[AlertsSuppressionRule]: ...

        @overload
        async def update(
                self, 
                alerts_suppression_rule_name: str, 
                alerts_suppression_rule: AlertsSuppressionRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertsSuppressionRule: ...

        @overload
        async def update(
                self, 
                alerts_suppression_rule_name: str, 
                alerts_suppression_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertsSuppressionRule: ...


    class azure.mgmt.security.aio.operations.AllowedConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                connection_type: Union[str, ConnectionType], 
                **kwargs: Any
            ) -> AllowedConnectionsResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[AllowedConnectionsResource]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AllowedConnectionsResource]: ...


    class azure.mgmt.security.aio.operations.ApplicationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                application_id: str, 
                application: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        async def create_or_update(
                self, 
                application_id: str, 
                application: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace_async
        async def delete(
                self, 
                application_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                application_id: str, 
                **kwargs: Any
            ) -> Application: ...


    class azure.mgmt.security.aio.operations.ApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Application]: ...


    class azure.mgmt.security.aio.operations.AssessmentsMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_in_subscription(
                self, 
                assessment_metadata_name: str, 
                assessment_metadata: SecurityAssessmentMetadataResponse, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityAssessmentMetadataResponse: ...

        @overload
        async def create_in_subscription(
                self, 
                assessment_metadata_name: str, 
                assessment_metadata: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityAssessmentMetadataResponse: ...

        @distributed_trace_async
        async def delete_in_subscription(
                self, 
                assessment_metadata_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                assessment_metadata_name: str, 
                **kwargs: Any
            ) -> SecurityAssessmentMetadataResponse: ...

        @distributed_trace_async
        async def get_in_subscription(
                self, 
                assessment_metadata_name: str, 
                **kwargs: Any
            ) -> SecurityAssessmentMetadataResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SecurityAssessmentMetadataResponse]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SecurityAssessmentMetadataResponse]: ...


    class azure.mgmt.security.aio.operations.AssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_id: str, 
                assessment_name: str, 
                assessment: SecurityAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityAssessmentResponse: ...

        @overload
        async def create_or_update(
                self, 
                resource_id: str, 
                assessment_name: str, 
                assessment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityAssessmentResponse: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_id: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_id: str, 
                assessment_name: str, 
                expand: Optional[Union[str, ExpandEnum]] = None, 
                **kwargs: Any
            ) -> SecurityAssessmentResponse: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityAssessmentResponse]: ...


    class azure.mgmt.security.aio.operations.AutoProvisioningSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                setting_name: str, 
                setting: AutoProvisioningSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoProvisioningSetting: ...

        @overload
        async def create(
                self, 
                setting_name: str, 
                setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoProvisioningSetting: ...

        @distributed_trace_async
        async def get(
                self, 
                setting_name: str, 
                **kwargs: Any
            ) -> AutoProvisioningSetting: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[AutoProvisioningSetting]: ...


    class azure.mgmt.security.aio.operations.AutomationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: Automation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Automation: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Automation: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                **kwargs: Any
            ) -> Automation: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Automation]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Automation]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: AutomationUpdateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Automation: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Automation: ...

        @overload
        async def validate(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: Automation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationValidationStatus: ...

        @overload
        async def validate(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationValidationStatus: ...


    class azure.mgmt.security.aio.operations.AzureDevOpsOrgsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                azure_dev_ops_org: AzureDevOpsOrg, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsOrg]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                azure_dev_ops_org: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsOrg]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                azure_dev_ops_org: AzureDevOpsOrg, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsOrg]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                azure_dev_ops_org: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsOrg]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                **kwargs: Any
            ) -> AzureDevOpsOrg: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureDevOpsOrg]: ...

        @distributed_trace_async
        async def list_available(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> AzureDevOpsOrgListResponse: ...


    class azure.mgmt.security.aio.operations.AzureDevOpsProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                azure_dev_ops_project: AzureDevOpsProject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsProject]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                azure_dev_ops_project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsProject]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                azure_dev_ops_project: AzureDevOpsProject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsProject]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                azure_dev_ops_project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsProject]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AzureDevOpsProject: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureDevOpsProject]: ...


    class azure.mgmt.security.aio.operations.AzureDevOpsReposOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                repo_name: str, 
                azure_dev_ops_repository: AzureDevOpsRepository, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsRepository]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                repo_name: str, 
                azure_dev_ops_repository: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsRepository]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                repo_name: str, 
                azure_dev_ops_repository: AzureDevOpsRepository, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsRepository]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                repo_name: str, 
                azure_dev_ops_repository: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsRepository]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                repo_name: str, 
                **kwargs: Any
            ) -> AzureDevOpsRepository: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureDevOpsRepository]: ...


    class azure.mgmt.security.aio.operations.ComplianceResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_id: str, 
                compliance_result_name: str, 
                **kwargs: Any
            ) -> ComplianceResult: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ComplianceResult]: ...


    class azure.mgmt.security.aio.operations.CompliancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                compliance_name: str, 
                **kwargs: Any
            ) -> Compliance: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Compliance]: ...


    class azure.mgmt.security.aio.operations.ConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                connector_name: str, 
                connector_setting: ConnectorSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectorSetting: ...

        @overload
        async def create_or_update(
                self, 
                connector_name: str, 
                connector_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectorSetting: ...

        @distributed_trace_async
        async def delete(
                self, 
                connector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                connector_name: str, 
                **kwargs: Any
            ) -> ConnectorSetting: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ConnectorSetting]: ...


    class azure.mgmt.security.aio.operations.CustomAssessmentAutomationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                custom_assessment_automation_name: str, 
                custom_assessment_automation_body: CustomAssessmentAutomationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomAssessmentAutomation: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                custom_assessment_automation_name: str, 
                custom_assessment_automation_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomAssessmentAutomation: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                custom_assessment_automation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                custom_assessment_automation_name: str, 
                **kwargs: Any
            ) -> CustomAssessmentAutomation: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CustomAssessmentAutomation]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[CustomAssessmentAutomation]: ...


    class azure.mgmt.security.aio.operations.CustomEntityStoreAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                custom_entity_store_assignment_name: str, 
                custom_entity_store_assignment_request_body: CustomEntityStoreAssignmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomEntityStoreAssignment: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                custom_entity_store_assignment_name: str, 
                custom_entity_store_assignment_request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomEntityStoreAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                custom_entity_store_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                custom_entity_store_assignment_name: str, 
                **kwargs: Any
            ) -> CustomEntityStoreAssignment: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CustomEntityStoreAssignment]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[CustomEntityStoreAssignment]: ...


    class azure.mgmt.security.aio.operations.CustomRecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                custom_recommendation_name: str, 
                custom_recommendation_body: CustomRecommendation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomRecommendation: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                custom_recommendation_name: str, 
                custom_recommendation_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomRecommendation: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                custom_recommendation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                custom_recommendation_name: str, 
                **kwargs: Any
            ) -> CustomRecommendation: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CustomRecommendation]: ...


    class azure.mgmt.security.aio.operations.DefenderForStorageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel_malware_scan(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                scan_id: str, 
                **kwargs: Any
            ) -> MalwareScan: ...

        @overload
        async def create(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                defender_for_storage_setting: DefenderForStorageSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @overload
        async def create(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                defender_for_storage_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @distributed_trace_async
        async def get_malware_scan(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                scan_id: str, 
                **kwargs: Any
            ) -> MalwareScan: ...

        @distributed_trace_async
        async def start_malware_scan(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                **kwargs: Any
            ) -> MalwareScan: ...


    class azure.mgmt.security.aio.operations.DevOpsConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                dev_ops_configuration: DevOpsConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevOpsConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                dev_ops_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevOpsConfiguration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                dev_ops_configuration: DevOpsConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevOpsConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                dev_ops_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevOpsConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> DevOpsConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DevOpsConfiguration]: ...


    class azure.mgmt.security.aio.operations.DevOpsOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                operation_result_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.security.aio.operations.DeviceSecurityGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_id: str, 
                device_security_group_name: str, 
                device_security_group: DeviceSecurityGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeviceSecurityGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_id: str, 
                device_security_group_name: str, 
                device_security_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeviceSecurityGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_id: str, 
                device_security_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_id: str, 
                device_security_group_name: str, 
                **kwargs: Any
            ) -> DeviceSecurityGroup: ...

        @distributed_trace
        def list(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeviceSecurityGroup]: ...


    class azure.mgmt.security.aio.operations.DiscoveredSecuritySolutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                discovered_security_solution_name: str, 
                **kwargs: Any
            ) -> DiscoveredSecuritySolution: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DiscoveredSecuritySolution]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DiscoveredSecuritySolution]: ...


    class azure.mgmt.security.aio.operations.ExternalSecuritySolutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                external_security_solutions_name: str, 
                **kwargs: Any
            ) -> ExternalSecuritySolution: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ExternalSecuritySolution]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExternalSecuritySolution]: ...


    class azure.mgmt.security.aio.operations.GitHubOwnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                **kwargs: Any
            ) -> GitHubOwner: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GitHubOwner]: ...

        @distributed_trace_async
        async def list_available(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> GitHubOwnerListResponse: ...


    class azure.mgmt.security.aio.operations.GitHubReposOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                repo_name: str, 
                **kwargs: Any
            ) -> GitHubRepository: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GitHubRepository]: ...


    class azure.mgmt.security.aio.operations.GitLabGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                group_fq_name: str, 
                **kwargs: Any
            ) -> GitLabGroup: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GitLabGroup]: ...

        @distributed_trace_async
        async def list_available(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> GitLabGroupListResponse: ...


    class azure.mgmt.security.aio.operations.GitLabProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                group_fq_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> GitLabProject: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                group_fq_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GitLabProject]: ...


    class azure.mgmt.security.aio.operations.GitLabSubgroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                group_fq_name: str, 
                **kwargs: Any
            ) -> GitLabGroupListResponse: ...


    class azure.mgmt.security.aio.operations.GovernanceAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                assessment_name: str, 
                assignment_key: str, 
                governance_assignment: GovernanceAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GovernanceAssignment: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                assessment_name: str, 
                assignment_key: str, 
                governance_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GovernanceAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                assessment_name: str, 
                assignment_key: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                assessment_name: str, 
                assignment_key: str, 
                **kwargs: Any
            ) -> GovernanceAssignment: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GovernanceAssignment]: ...


    class azure.mgmt.security.aio.operations.GovernanceRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                scope: str, 
                rule_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_execute(
                self, 
                scope: str, 
                rule_id: str, 
                execute_governance_rule_params: Optional[ExecuteGovernanceRuleParams] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_execute(
                self, 
                scope: str, 
                rule_id: str, 
                execute_governance_rule_params: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                rule_id: str, 
                governance_rule: GovernanceRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GovernanceRule: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                rule_id: str, 
                governance_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GovernanceRule: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                rule_id: str, 
                **kwargs: Any
            ) -> GovernanceRule: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GovernanceRule]: ...

        @distributed_trace_async
        async def operation_results(
                self, 
                scope: str, 
                rule_id: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[OperationResultAutoGenerated]: ...


    class azure.mgmt.security.aio.operations.HealthReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_id: str, 
                health_report_name: str, 
                **kwargs: Any
            ) -> HealthReport: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HealthReport]: ...


    class azure.mgmt.security.aio.operations.InformationProtectionPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                information_protection_policy_name: Union[str, InformationProtectionPolicyName], 
                information_protection_policy: InformationProtectionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformationProtectionPolicy: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                information_protection_policy_name: Union[str, InformationProtectionPolicyName], 
                information_protection_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformationProtectionPolicy: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                information_protection_policy_name: Union[str, InformationProtectionPolicyName], 
                **kwargs: Any
            ) -> InformationProtectionPolicy: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[InformationProtectionPolicy]: ...


    class azure.mgmt.security.aio.operations.IotSecuritySolutionAnalyticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> IoTSecuritySolutionAnalyticsModel: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> IoTSecuritySolutionAnalyticsModelList: ...


    class azure.mgmt.security.aio.operations.IotSecuritySolutionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                iot_security_solution_data: IoTSecuritySolutionModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IoTSecuritySolutionModel: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                iot_security_solution_data: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IoTSecuritySolutionModel: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> IoTSecuritySolutionModel: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[IoTSecuritySolutionModel]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[IoTSecuritySolutionModel]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                update_iot_security_solution_data: UpdateIotSecuritySolutionData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IoTSecuritySolutionModel: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                update_iot_security_solution_data: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IoTSecuritySolutionModel: ...


    class azure.mgmt.security.aio.operations.IotSecuritySolutionsAnalyticsAggregatedAlertOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def dismiss(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                aggregated_alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                aggregated_alert_name: str, 
                **kwargs: Any
            ) -> IoTSecurityAggregatedAlert: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[IoTSecurityAggregatedAlert]: ...


    class azure.mgmt.security.aio.operations.IotSecuritySolutionsAnalyticsRecommendationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                aggregated_recommendation_name: str, 
                **kwargs: Any
            ) -> IoTSecurityAggregatedRecommendation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[IoTSecurityAggregatedRecommendation]: ...


    class azure.mgmt.security.aio.operations.JitNetworkAccessPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                body: JitNetworkAccessPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitNetworkAccessPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitNetworkAccessPolicy: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                **kwargs: Any
            ) -> JitNetworkAccessPolicy: ...

        @overload
        async def initiate(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                body: JitNetworkAccessPolicyInitiateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitNetworkAccessRequest: ...

        @overload
        async def initiate(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitNetworkAccessRequest: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[JitNetworkAccessPolicy]: ...

        @distributed_trace
        def list_by_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JitNetworkAccessPolicy]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JitNetworkAccessPolicy]: ...

        @distributed_trace
        def list_by_resource_group_and_region(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JitNetworkAccessPolicy]: ...


    class azure.mgmt.security.aio.operations.LocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> AscLocation: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[AscLocation]: ...


    class azure.mgmt.security.aio.operations.MdeOnboardingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(self, **kwargs: Any) -> MdeOnboardingData: ...

        @distributed_trace_async
        async def list(self, **kwargs: Any) -> MdeOnboardingDataList: ...


    class azure.mgmt.security.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.security.aio.operations.PricingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope_id: str, 
                pricing_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope_id: str, 
                pricing_name: str, 
                **kwargs: Any
            ) -> Pricing: ...

        @distributed_trace_async
        async def list(
                self, 
                scope_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> PricingList: ...

        @overload
        async def update(
                self, 
                scope_id: str, 
                pricing_name: str, 
                pricing: Pricing, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Pricing: ...

        @overload
        async def update(
                self, 
                scope_id: str, 
                pricing_name: str, 
                pricing: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Pricing: ...


    class azure.mgmt.security.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.security.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                group_id: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> PrivateLinkResourceAutoGenerated: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResourceAutoGenerated]: ...


    class azure.mgmt.security.aio.operations.PrivateLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_link: PrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateLinkResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_link: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateLinkResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace_async
        async def head(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[PrivateLinkResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_link: PrivateLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_link: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...


    class azure.mgmt.security.aio.operations.RegulatoryComplianceAssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                regulatory_compliance_standard_name: str, 
                regulatory_compliance_control_name: str, 
                regulatory_compliance_assessment_name: str, 
                **kwargs: Any
            ) -> RegulatoryComplianceAssessment: ...

        @distributed_trace
        def list(
                self, 
                regulatory_compliance_standard_name: str, 
                regulatory_compliance_control_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RegulatoryComplianceAssessment]: ...


    class azure.mgmt.security.aio.operations.RegulatoryComplianceControlsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                regulatory_compliance_standard_name: str, 
                regulatory_compliance_control_name: str, 
                **kwargs: Any
            ) -> RegulatoryComplianceControl: ...

        @distributed_trace
        def list(
                self, 
                regulatory_compliance_standard_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RegulatoryComplianceControl]: ...


    class azure.mgmt.security.aio.operations.RegulatoryComplianceStandardsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                regulatory_compliance_standard_name: str, 
                **kwargs: Any
            ) -> RegulatoryComplianceStandard: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RegulatoryComplianceStandard]: ...


    class azure.mgmt.security.aio.operations.SecureScoreControlDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SecureScoreControlDefinitionItem]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SecureScoreControlDefinitionItem]: ...


    class azure.mgmt.security.aio.operations.SecureScoreControlsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                expand: Optional[Union[str, ExpandControlsEnum]] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecureScoreControlDetails]: ...

        @distributed_trace
        def list_by_secure_score(
                self, 
                secure_score_name: str, 
                expand: Optional[Union[str, ExpandControlsEnum]] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecureScoreControlDetails]: ...


    class azure.mgmt.security.aio.operations.SecureScoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                secure_score_name: str, 
                **kwargs: Any
            ) -> SecureScoreItem: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SecureScoreItem]: ...


    class azure.mgmt.security.aio.operations.SecurityConnectorApplicationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                application_id: str, 
                application: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                application_id: str, 
                application: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                application_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                application_id: str, 
                **kwargs: Any
            ) -> Application: ...


    class azure.mgmt.security.aio.operations.SecurityConnectorApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Application]: ...


    class azure.mgmt.security.aio.operations.SecurityConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                security_connector: SecurityConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityConnector: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                security_connector: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityConnector: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> SecurityConnector: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SecurityConnector]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityConnector]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                security_connector: SecurityConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityConnector: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                security_connector: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityConnector: ...


    class azure.mgmt.security.aio.operations.SecurityContactsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                security_contact_name: Union[str, SecurityContactName], 
                security_contact: SecurityContact, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityContact: ...

        @overload
        async def create(
                self, 
                security_contact_name: Union[str, SecurityContactName], 
                security_contact: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityContact: ...

        @distributed_trace_async
        async def delete(
                self, 
                security_contact_name: Union[str, SecurityContactName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                security_contact_name: Union[str, SecurityContactName], 
                **kwargs: Any
            ) -> SecurityContact: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SecurityContact]: ...


    class azure.mgmt.security.aio.operations.SecurityOperatorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create_or_update(
                self, 
                pricing_name: str, 
                security_operator_name: str, 
                **kwargs: Any
            ) -> SecurityOperator: ...

        @distributed_trace_async
        async def delete(
                self, 
                pricing_name: str, 
                security_operator_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                pricing_name: str, 
                security_operator_name: str, 
                **kwargs: Any
            ) -> SecurityOperator: ...

        @distributed_trace_async
        async def list(
                self, 
                pricing_name: str, 
                **kwargs: Any
            ) -> SecurityOperatorList: ...


    class azure.mgmt.security.aio.operations.SecuritySolutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                security_solution_name: str, 
                **kwargs: Any
            ) -> SecuritySolution: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SecuritySolution]: ...


    class azure.mgmt.security.aio.operations.SecuritySolutionsReferenceDataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(self, **kwargs: Any) -> SecuritySolutionsReferenceDataList: ...

        @distributed_trace_async
        async def list_by_home_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> SecuritySolutionsReferenceDataList: ...


    class azure.mgmt.security.aio.operations.SecurityStandardsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                standard_id: str, 
                standard: SecurityStandard, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityStandard: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                standard_id: str, 
                standard: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityStandard: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                standard_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                standard_id: str, 
                **kwargs: Any
            ) -> SecurityStandard: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityStandard]: ...


    class azure.mgmt.security.aio.operations.SensitivitySettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                sensitivity_settings: UpdateSensitivitySettingsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetSensitivitySettingsResponse: ...

        @overload
        async def create_or_update(
                self, 
                sensitivity_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetSensitivitySettingsResponse: ...

        @distributed_trace_async
        async def get(self, **kwargs: Any) -> GetSensitivitySettingsResponse: ...

        @distributed_trace_async
        async def list(self, **kwargs: Any) -> GetSensitivitySettingsListResponse: ...


    class azure.mgmt.security.aio.operations.ServerVulnerabilityAssessmentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessment: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessment: ...

        @distributed_trace_async
        async def list_by_extended_resource(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessmentsList: ...


    class azure.mgmt.security.aio.operations.ServerVulnerabilityAssessmentsSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                setting_kind: Union[str, ServerVulnerabilityAssessmentsSettingKindName], 
                server_vulnerability_assessments_setting: ServerVulnerabilityAssessmentsSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessmentsSetting: ...

        @overload
        async def create_or_update(
                self, 
                setting_kind: Union[str, ServerVulnerabilityAssessmentsSettingKindName], 
                server_vulnerability_assessments_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessmentsSetting: ...

        @distributed_trace_async
        async def delete(
                self, 
                setting_kind: Union[str, ServerVulnerabilityAssessmentsSettingKindName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                setting_kind: Union[str, ServerVulnerabilityAssessmentsSettingKindName], 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessmentsSetting: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ServerVulnerabilityAssessmentsSetting]: ...


    class azure.mgmt.security.aio.operations.SettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                setting_name: Union[str, SettingNameAutoGenerated], 
                **kwargs: Any
            ) -> Setting: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Setting]: ...

        @overload
        async def update(
                self, 
                setting_name: Union[str, SettingNameAutoGenerated], 
                setting: Setting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @overload
        async def update(
                self, 
                setting_name: Union[str, SettingNameAutoGenerated], 
                setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...


    class azure.mgmt.security.aio.operations.SoftwareInventoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                software_name: str, 
                **kwargs: Any
            ) -> Software: ...

        @distributed_trace
        def list_by_extended_resource(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Software]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Software]: ...


    class azure.mgmt.security.aio.operations.SqlVulnerabilityAssessmentBaselineRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add(
                self, 
                workspace_id: str, 
                resource_id: str, 
                body: Optional[RulesResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RulesResults: ...

        @overload
        async def add(
                self, 
                workspace_id: str, 
                resource_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RulesResults: ...

        @overload
        async def create_or_update(
                self, 
                rule_id: str, 
                workspace_id: str, 
                resource_id: str, 
                body: Optional[RuleResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuleResults: ...

        @overload
        async def create_or_update(
                self, 
                rule_id: str, 
                workspace_id: str, 
                resource_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuleResults: ...

        @distributed_trace_async
        async def delete(
                self, 
                rule_id: str, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                rule_id: str, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> RuleResults: ...

        @distributed_trace_async
        async def list(
                self, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> RulesResults: ...


    class azure.mgmt.security.aio.operations.SqlVulnerabilityAssessmentScanResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scan_id: str, 
                scan_result_id: str, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> ScanResult: ...

        @distributed_trace_async
        async def list(
                self, 
                scan_id: str, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> ScanResults: ...


    class azure.mgmt.security.aio.operations.SqlVulnerabilityAssessmentScansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scan_id: str, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> Scan: ...

        @distributed_trace_async
        async def list(
                self, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> Scans: ...


    class azure.mgmt.security.aio.operations.StandardAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_id: str, 
                standard_assignment_name: str, 
                standard_assignment: StandardAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandardAssignment: ...

        @overload
        async def create(
                self, 
                resource_id: str, 
                standard_assignment_name: str, 
                standard_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandardAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_id: str, 
                standard_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_id: str, 
                standard_assignment_name: str, 
                **kwargs: Any
            ) -> StandardAssignment: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StandardAssignment]: ...


    class azure.mgmt.security.aio.operations.SubAssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                assessment_name: str, 
                sub_assessment_name: str, 
                **kwargs: Any
            ) -> SecuritySubAssessment: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecuritySubAssessment]: ...

        @distributed_trace
        def list_all(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecuritySubAssessment]: ...


    class azure.mgmt.security.aio.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_resource_group_level_task(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                task_name: str, 
                **kwargs: Any
            ) -> SecurityTask: ...

        @distributed_trace_async
        async def get_subscription_level_task(
                self, 
                asc_location: str, 
                task_name: str, 
                **kwargs: Any
            ) -> SecurityTask: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityTask]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityTask]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityTask]: ...

        @distributed_trace_async
        async def update_resource_group_level_task_state(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                task_name: str, 
                task_update_action_type: Union[str, TaskUpdateActionType], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_subscription_level_task_state(
                self, 
                asc_location: str, 
                task_name: str, 
                task_update_action_type: Union[str, TaskUpdateActionType], 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.security.aio.operations.TopologyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                topology_resource_name: str, 
                **kwargs: Any
            ) -> TopologyResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[TopologyResource]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TopologyResource]: ...


    class azure.mgmt.security.aio.operations.WorkspaceSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                workspace_setting_name: str, 
                workspace_setting: WorkspaceSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceSetting: ...

        @overload
        async def create(
                self, 
                workspace_setting_name: str, 
                workspace_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceSetting: ...

        @distributed_trace_async
        async def delete(
                self, 
                workspace_setting_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                workspace_setting_name: str, 
                **kwargs: Any
            ) -> WorkspaceSetting: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[WorkspaceSetting]: ...

        @overload
        async def update(
                self, 
                workspace_setting_name: str, 
                workspace_setting: WorkspaceSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceSetting: ...

        @overload
        async def update(
                self, 
                workspace_setting_name: str, 
                workspace_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceSetting: ...


namespace azure.mgmt.security.models

    class azure.mgmt.security.models.AadConnectivityState(Model):
        connectivity_state: Union[str, AadConnectivityStateEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connectivity_state: Optional[Union[str, AadConnectivityStateEnum]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AadConnectivityStateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCOVERED = "Discovered"
        NOT_LICENSED = "NotLicensed"


    class azure.mgmt.security.models.AadExternalSecuritySolution(ExternalSecuritySolution):
        id: str
        kind: Union[str, ExternalSecuritySolutionKindEnum]
        location: str
        name: str
        properties: AadSolutionProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ExternalSecuritySolutionKindEnum]] = ..., 
                properties: Optional[AadSolutionProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AadSolutionProperties(ExternalSecuritySolutionProperties, AadConnectivityState):
        additional_properties: dict[str, any]
        connectivity_state: Union[str, AadConnectivityStateEnum]
        device_type: str
        device_vendor: str
        workspace: ConnectedWorkspace

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                connectivity_state: Optional[Union[str, AadConnectivityStateEnum]] = ..., 
                device_type: Optional[str] = ..., 
                device_vendor: Optional[str] = ..., 
                workspace: Optional[ConnectedWorkspace] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AccessTokenAuthentication(Authentication):
        access_token: str
        authentication_type: Union[str, AuthenticationType]
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_token: Optional[str] = ..., 
                username: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_HUB = "EventHub"
        INTERNAL = "Internal"
        LOGIC_APP = "LogicApp"
        WORKSPACE = "Workspace"


    class azure.mgmt.security.models.ActionableRemediation(Model):
        branch_configuration: TargetBranchConfiguration
        category_configurations: list[CategoryConfiguration]
        inherit_from_parent_state: Union[str, InheritFromParentState]
        state: Union[str, ActionableRemediationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                branch_configuration: Optional[TargetBranchConfiguration] = ..., 
                category_configurations: Optional[List[CategoryConfiguration]] = ..., 
                inherit_from_parent_state: Optional[Union[str, InheritFromParentState]] = ..., 
                state: Optional[Union[str, ActionableRemediationState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ActionableRemediationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NONE = "None"


    class azure.mgmt.security.models.ActiveConnectionsNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AdditionalData(Model):
        assessed_resource_type: Union[str, AssessedResourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AdditionalWorkspaceDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"
        RAW_EVENTS = "RawEvents"


    class azure.mgmt.security.models.AdditionalWorkspaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SENTINEL = "Sentinel"


    class azure.mgmt.security.models.AdditionalWorkspacesProperties(Model):
        data_types: Union[list[str, AdditionalWorkspaceDataType]]
        type: Union[str, AdditionalWorkspaceType]
        workspace: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_types: Optional[List[Union[str, AdditionalWorkspaceDataType]]] = ..., 
                type: Union[str, AdditionalWorkspaceType] = "Sentinel", 
                workspace: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AdvancedThreatProtectionSetting(Resource):
        id: str
        is_enabled: bool
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AgentlessConfiguration(Model):
        agentless_auto_discovery: Union[str, AutoDiscovery]
        agentless_enabled: Union[str, AgentlessEnablement]
        inventory_list: list[InventoryList]
        inventory_list_type: Union[str, InventoryListKind]
        scanners: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agentless_auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                agentless_enabled: Optional[Union[str, AgentlessEnablement]] = ..., 
                inventory_list: Optional[List[InventoryList]] = ..., 
                inventory_list_type: Optional[Union[str, InventoryListKind]] = ..., 
                scanners: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AgentlessEnablement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.security.models.Alert(Resource):
        alert_display_name: str
        alert_type: str
        alert_uri: str
        compromised_entity: str
        correlation_key: str
        description: str
        end_time_utc: datetime
        entities: list[AlertEntity]
        extended_links: list[dict[str, str]]
        extended_properties: dict[str, str]
        id: str
        intent: Union[str, Intent]
        is_incident: bool
        name: str
        processing_end_time_utc: datetime
        product_component_name: str
        product_name: str
        remediation_steps: list[str]
        resource_identifiers: list[ResourceIdentifier]
        severity: Union[str, AlertSeverity]
        start_time_utc: datetime
        status: Union[str, AlertStatus]
        sub_techniques: list[str]
        supporting_evidence: AlertPropertiesSupportingEvidence
        system_alert_id: str
        techniques: list[str]
        time_generated_utc: datetime
        type: str
        vendor_name: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_properties: Optional[Dict[str, str]] = ..., 
                supporting_evidence: Optional[AlertPropertiesSupportingEvidence] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AlertEntity(Model):
        additional_properties: dict[str, JSON]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AlertList(Model):
        next_link: str
        value: list[Alert]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Alert]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AlertPropertiesSupportingEvidence(Model):
        additional_properties: dict[str, JSON]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AlertSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        INFORMATIONAL = "Informational"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.AlertSimulatorBundlesRequestProperties(AlertSimulatorRequestProperties):
        additional_properties: dict[str, any]
        bundles: Union[list[str, BundleType]]
        kind: Union[str, KindEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                bundles: Optional[List[Union[str, BundleType]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AlertSimulatorRequestBody(Model):
        properties: AlertSimulatorRequestProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AlertSimulatorRequestProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AlertSimulatorRequestProperties(Model):
        additional_properties: dict[str, any]
        kind: Union[str, KindEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AlertStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DISMISSED = "Dismissed"
        IN_PROGRESS = "InProgress"
        RESOLVED = "Resolved"


    class azure.mgmt.security.models.AlertSyncSettings(Setting):
        enabled: bool
        id: str
        kind: Union[str, SettingKind]
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AlertsSuppressionRule(Resource):
        alert_type: str
        comment: str
        expiration_date_utc: datetime
        id: str
        last_modified_utc: datetime
        name: str
        reason: str
        state: Union[str, RuleState]
        suppression_alerts_scope: SuppressionAlertsScope
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                alert_type: Optional[str] = ..., 
                comment: Optional[str] = ..., 
                expiration_date_utc: Optional[datetime] = ..., 
                reason: Optional[str] = ..., 
                state: Optional[Union[str, RuleState]] = ..., 
                suppression_alerts_scope: Optional[SuppressionAlertsScope] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AlertsSuppressionRulesList(Model):
        next_link: str
        value: list[AlertsSuppressionRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[AlertsSuppressionRule], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AllowedConnectionsList(Model):
        next_link: str
        value: list[AllowedConnectionsResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AllowedConnectionsResource(Resource, Location):
        calculated_date_time: datetime
        connectable_resources: list[ConnectableResource]
        id: str
        location: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AllowlistCustomAlertRule(ListCustomAlertRule):
        allowlist_values: list[str]
        description: str
        display_name: str
        is_enabled: bool
        rule_type: str
        value_type: Union[str, ValueType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowlist_values: List[str], 
                is_enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AmqpC2DMessagesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AmqpC2DRejectedMessagesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AmqpD2CMessagesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AnnotateDefaultBranchState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.ApiCollection(Resource):
        base_url: str
        discovered_via: str
        display_name: str
        id: str
        name: str
        number_of_api_endpoints: int
        number_of_api_endpoints_with_sensitive_data_exposed: int
        number_of_external_api_endpoints: int
        number_of_inactive_api_endpoints: int
        number_of_unauthenticated_api_endpoints: int
        provisioning_state: Union[str, ProvisioningState]
        sensitivity_label: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ApiCollectionList(Model):
        next_link: str
        value: list[ApiCollection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Application(Resource):
        condition_sets: list[JSON]
        description: str
        display_name: str
        id: str
        name: str
        source_resource_type: Union[str, ApplicationSourceResourceType]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                condition_sets: Optional[List[JSON]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                source_resource_type: Optional[Union[str, ApplicationSourceResourceType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ApplicationCondition(Model):
        operator: Union[str, ApplicationConditionOperator]
        property: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operator: Optional[Union[str, ApplicationConditionOperator]] = ..., 
                property: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ApplicationConditionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "Contains"
        EQUALS = "Equals"
        IN = "In"
        IN_ENUM = "In"


    class azure.mgmt.security.models.ApplicationSourceResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSESSMENTS = "Assessments"


    class azure.mgmt.security.models.ApplicationsList(Model):
        next_link: str
        value: list[Application]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ArcAutoProvisioning(Model):
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ArcAutoProvisioningAws(ArcAutoProvisioning):
        cloud_role_arn: str
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ArcAutoProvisioningConfiguration(Model):
        private_link_scope: str
        proxy: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_link_scope: Optional[str] = ..., 
                proxy: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ArcAutoProvisioningGcp(ArcAutoProvisioning):
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AscLocation(Resource):
        id: str
        name: str
        properties: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AscLocationList(Model):
        next_link: str
        value: list[AscLocation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AssessedResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_REGISTRY_VULNERABILITY = "ContainerRegistryVulnerability"
        SERVER_VULNERABILITY = "ServerVulnerability"
        SQL_SERVER_VULNERABILITY = "SqlServerVulnerability"


    class azure.mgmt.security.models.AssessmentLinks(Model):
        azure_portal_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AssessmentStatus(Model):
        cause: str
        code: Union[str, AssessmentStatusCode]
        description: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cause: Optional[str] = ..., 
                code: Union[str, AssessmentStatusCode], 
                description: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AssessmentStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_APPLICABLE = "NotApplicable"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.security.models.AssessmentStatusResponse(AssessmentStatus):
        cause: str
        code: Union[str, AssessmentStatusCode]
        description: str
        first_evaluation_date: datetime
        status_change_date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cause: Optional[str] = ..., 
                code: Union[str, AssessmentStatusCode], 
                description: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AssessmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN = "BuiltIn"
        BUILT_IN_POLICY = "BuiltInPolicy"
        CUSTOMER_MANAGED = "CustomerManaged"
        CUSTOM_POLICY = "CustomPolicy"
        DYNAMIC_BUILT_IN = "DynamicBuiltIn"
        MANUAL_BUILT_IN = "ManualBuiltIn"
        MANUAL_BUILT_IN_POLICY = "ManualBuiltInPolicy"
        MANUAL_CUSTOM_POLICY = "ManualCustomPolicy"
        VERIFIED_PARTNER = "VerifiedPartner"


    class azure.mgmt.security.models.AssignedAssessmentItem(Model):
        assessment_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AssignedStandardItem(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AtaExternalSecuritySolution(ExternalSecuritySolution):
        id: str
        kind: Union[str, ExternalSecuritySolutionKindEnum]
        location: str
        name: str
        properties: AtaSolutionProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ExternalSecuritySolutionKindEnum]] = ..., 
                properties: Optional[AtaSolutionProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AtaSolutionProperties(ExternalSecuritySolutionProperties):
        additional_properties: dict[str, any]
        device_type: str
        device_vendor: str
        last_event_received: str
        workspace: ConnectedWorkspace

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                device_type: Optional[str] = ..., 
                device_vendor: Optional[str] = ..., 
                last_event_received: Optional[str] = ..., 
                workspace: Optional[ConnectedWorkspace] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AttestationComplianceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANT = "compliant"
        NON_COMPLIANT = "nonCompliant"
        UNKNOWN = "unknown"


    class azure.mgmt.security.models.AttestationEvidence(Model):
        description: str
        source_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                source_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Authentication(Model):
        authentication_type: Union[str, AuthenticationType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AuthenticationDetailsProperties(Model):
        authentication_provisioning_state: Union[str, AuthenticationProvisioningState]
        authentication_type: Union[str, AuthenticationType]
        granted_permissions: Union[list[str, PermissionProperty]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AuthenticationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPIRED = "Expired"
        INCORRECT_POLICY = "IncorrectPolicy"
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.security.models.AuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS_ASSUME_ROLE = "awsAssumeRole"
        AWS_CREDS = "awsCreds"
        GCP_CREDENTIALS = "gcpCredentials"


    class azure.mgmt.security.models.Authorization(Model):
        code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutoDiscovery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.security.models.AutoProvision(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.security.models.AutoProvisioningSetting(Resource):
        auto_provision: Union[str, AutoProvision]
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_provision: Optional[Union[str, AutoProvision]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutoProvisioningSettingList(Model):
        next_link: str
        value: list[AutoProvisioningSetting]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[AutoProvisioningSetting]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Automation(TrackedResource):
        actions: list[AutomationAction]
        description: str
        etag: str
        id: str
        is_enabled: bool
        kind: str
        location: str
        name: str
        scopes: list[AutomationScope]
        sources: list[AutomationSource]
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[AutomationAction]] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                scopes: Optional[List[AutomationScope]] = ..., 
                sources: Optional[List[AutomationSource]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationAction(Model):
        action_type: Union[str, ActionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationActionEventHub(AutomationAction):
        action_type: Union[str, ActionType]
        connection_string: str
        event_hub_resource_id: str
        is_trusted_service_enabled: bool
        sas_policy_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_string: Optional[str] = ..., 
                event_hub_resource_id: Optional[str] = ..., 
                is_trusted_service_enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationActionLogicApp(AutomationAction):
        action_type: Union[str, ActionType]
        logic_app_resource_id: str
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                logic_app_resource_id: Optional[str] = ..., 
                uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationActionWorkspace(AutomationAction):
        action_type: Union[str, ActionType]
        workspace_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                workspace_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationList(Model):
        next_link: str
        value: list[Automation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[Automation], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationRuleSet(Model):
        rules: list[AutomationTriggeringRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                rules: Optional[List[AutomationTriggeringRule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationScope(Model):
        description: str
        scope_path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                scope_path: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationSource(Model):
        event_source: Union[str, EventSource]
        rule_sets: list[AutomationRuleSet]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_source: Optional[Union[str, EventSource]] = ..., 
                rule_sets: Optional[List[AutomationRuleSet]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationTriggeringRule(Model):
        expected_value: str
        operator: Union[str, Operator]
        property_j_path: str
        property_type: Union[str, PropertyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expected_value: Optional[str] = ..., 
                operator: Optional[Union[str, Operator]] = ..., 
                property_j_path: Optional[str] = ..., 
                property_type: Optional[Union[str, PropertyType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationUpdateModel(Tags):
        actions: list[AutomationAction]
        description: str
        is_enabled: bool
        scopes: list[AutomationScope]
        sources: list[AutomationSource]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[AutomationAction]] = ..., 
                description: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                scopes: Optional[List[AutomationScope]] = ..., 
                sources: Optional[List[AutomationSource]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AutomationValidationStatus(Model):
        is_valid: bool
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_valid: Optional[bool] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AwAssumeRoleAuthenticationDetailsProperties(AuthenticationDetailsProperties):
        account_id: str
        authentication_provisioning_state: Union[str, AuthenticationProvisioningState]
        authentication_type: Union[str, AuthenticationType]
        aws_assume_role_arn: str
        aws_external_id: str
        granted_permissions: Union[list[str, PermissionProperty]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aws_assume_role_arn: str, 
                aws_external_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AwsCredsAuthenticationDetailsProperties(AuthenticationDetailsProperties):
        account_id: str
        authentication_provisioning_state: Union[str, AuthenticationProvisioningState]
        authentication_type: Union[str, AuthenticationType]
        aws_access_key_id: str
        aws_secret_access_key: str
        granted_permissions: Union[list[str, PermissionProperty]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aws_access_key_id: str, 
                aws_secret_access_key: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AwsEnvironmentData(EnvironmentData):
        account_name: str
        environment_type: Union[str, EnvironmentType]
        organizational_data: AwsOrganizationalData
        regions: list[str]
        scan_interval: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                organizational_data: Optional[AwsOrganizationalData] = ..., 
                regions: Optional[List[str]] = ..., 
                scan_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AwsOrganizationalData(Model):
        organization_membership_type: Union[str, OrganizationMembershipType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AwsOrganizationalDataMaster(AwsOrganizationalData):
        excluded_account_ids: list[str]
        organization_membership_type: Union[str, OrganizationMembershipType]
        stackset_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                excluded_account_ids: Optional[List[str]] = ..., 
                stackset_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AwsOrganizationalDataMember(AwsOrganizationalData):
        organization_membership_type: Union[str, OrganizationMembershipType]
        parent_hierarchy_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parent_hierarchy_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsOrg(ProxyResource):
        id: str
        name: str
        properties: AzureDevOpsOrgProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AzureDevOpsOrgProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsOrgListResponse(Model):
        next_link: str
        value: list[AzureDevOpsOrg]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AzureDevOpsOrg]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsOrgProperties(Model):
        actionable_remediation: ActionableRemediation
        onboarding_state: Union[str, OnboardingState]
        provisioning_state: Union[str, DevOpsProvisioningState]
        provisioning_status_message: str
        provisioning_status_update_time_utc: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actionable_remediation: Optional[ActionableRemediation] = ..., 
                onboarding_state: Optional[Union[str, OnboardingState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsOrganizationConfiguration(Model):
        auto_discovery: Union[str, AutoDiscovery]
        project_configs: dict[str, AzureDevOpsProjectConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                project_configs: Optional[Dict[str, AzureDevOpsProjectConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsProject(ProxyResource):
        id: str
        name: str
        properties: AzureDevOpsProjectProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AzureDevOpsProjectProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsProjectConfiguration(Model):
        auto_discovery: Union[str, AutoDiscovery]
        repository_configs: dict[str, BaseResourceConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                repository_configs: Optional[Dict[str, BaseResourceConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsProjectListResponse(Model):
        next_link: str
        value: list[AzureDevOpsProject]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AzureDevOpsProject]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsProjectProperties(Model):
        actionable_remediation: ActionableRemediation
        onboarding_state: Union[str, OnboardingState]
        parent_org_name: str
        project_id: str
        provisioning_state: Union[str, DevOpsProvisioningState]
        provisioning_status_message: str
        provisioning_status_update_time_utc: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actionable_remediation: Optional[ActionableRemediation] = ..., 
                onboarding_state: Optional[Union[str, OnboardingState]] = ..., 
                parent_org_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsRepository(ProxyResource):
        id: str
        name: str
        properties: AzureDevOpsRepositoryProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AzureDevOpsRepositoryProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsRepositoryListResponse(Model):
        next_link: str
        value: list[AzureDevOpsRepository]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AzureDevOpsRepository]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsRepositoryProperties(Model):
        actionable_remediation: ActionableRemediation
        onboarding_state: Union[str, OnboardingState]
        parent_org_name: str
        parent_project_name: str
        provisioning_state: Union[str, DevOpsProvisioningState]
        provisioning_status_message: str
        provisioning_status_update_time_utc: datetime
        repo_id: str
        repo_url: str
        visibility: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actionable_remediation: Optional[ActionableRemediation] = ..., 
                onboarding_state: Optional[Union[str, OnboardingState]] = ..., 
                parent_org_name: Optional[str] = ..., 
                parent_project_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureDevOpsScopeEnvironmentData(EnvironmentData):
        environment_type: Union[str, EnvironmentType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureResourceDetails(ResourceDetails):
        id: str
        source: Union[str, Source]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureResourceIdentifier(ResourceIdentifier):
        azure_resource_id: str
        type: Union[str, ResourceIdentifierType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureResourceLink(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureServersSetting(ServerVulnerabilityAssessmentsSetting):
        id: str
        kind: Union[str, ServerVulnerabilityAssessmentsSettingKind]
        name: str
        selected_provider: Union[str, ServerVulnerabilityAssessmentsAzureSettingSelectedProvider]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                selected_provider: Optional[Union[str, ServerVulnerabilityAssessmentsAzureSettingSelectedProvider]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.AzureTrackedResourceLocation(Model):
        location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.BaseResourceConfiguration(Model):
        desired_onboarding_state: Union[str, DesiredOnboardingState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                desired_onboarding_state: Optional[Union[str, DesiredOnboardingState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Baseline(Model):
        expected_results: list[list[str]]
        updated_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expected_results: Optional[List[List[str]]] = ..., 
                updated_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.BaselineAdjustedResult(Model):
        baseline: Baseline
        results_not_in_baseline: list[list[str]]
        results_only_in_baseline: list[list[str]]
        status: Union[str, RuleStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                baseline: Optional[Baseline] = ..., 
                results_not_in_baseline: Optional[List[List[str]]] = ..., 
                results_only_in_baseline: Optional[List[List[str]]] = ..., 
                status: Optional[Union[str, RuleStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.BenchmarkReference(Model):
        benchmark: str
        reference: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                benchmark: Optional[str] = ..., 
                reference: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.BlobScanResultsOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_INDEX_TAGS = "blobIndexTags"
        NONE = "None"


    class azure.mgmt.security.models.BlobsScanSummary(Model):
        failed_blobs_count: int
        malicious_blobs_count: int
        scanned_blobs_in_gb: float
        skipped_blobs_count: int
        total_blobs_scanned: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                failed_blobs_count: Optional[int] = ..., 
                malicious_blobs_count: Optional[int] = ..., 
                scanned_blobs_in_gb: Optional[float] = ..., 
                skipped_blobs_count: Optional[int] = ..., 
                total_blobs_scanned: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.BuiltInInfoType(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.BundleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP_SERVICES = "AppServices"
        COSMOS_DBS = "CosmosDbs"
        DNS = "DNS"
        KEY_VAULTS = "KeyVaults"
        KUBERNETES_SERVICE = "KubernetesService"
        RESOURCE_MANAGER = "ResourceManager"
        SQL_SERVERS = "SqlServers"
        STORAGE_ACCOUNTS = "StorageAccounts"
        VIRTUAL_MACHINES = "VirtualMachines"


    class azure.mgmt.security.models.CVE(Model):
        link: str
        title: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CVSS(Model):
        base: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Categories(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP_SERVICES = "AppServices"
        COMPUTE = "Compute"
        CONTAINER = "Container"
        DATA = "Data"
        IDENTITY_AND_ACCESS = "IdentityAndAccess"
        IO_T = "IoT"
        NETWORKING = "Networking"


    class azure.mgmt.security.models.CategoryConfiguration(Model):
        category: Union[str, RuleCategory]
        minimum_severity_level: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[Union[str, RuleCategory]] = ..., 
                minimum_severity_level: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CefExternalSecuritySolution(ExternalSecuritySolution):
        id: str
        kind: Union[str, ExternalSecuritySolutionKindEnum]
        location: str
        name: str
        properties: CefSolutionProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ExternalSecuritySolutionKindEnum]] = ..., 
                properties: Optional[CefSolutionProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CefSolutionProperties(ExternalSecuritySolutionProperties):
        additional_properties: dict[str, any]
        agent: str
        device_type: str
        device_vendor: str
        hostname: str
        last_event_received: str
        workspace: ConnectedWorkspace

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                agent: Optional[str] = ..., 
                device_type: Optional[str] = ..., 
                device_vendor: Optional[str] = ..., 
                hostname: Optional[str] = ..., 
                last_event_received: Optional[str] = ..., 
                workspace: Optional[ConnectedWorkspace] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CloudErrorBody(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CloudName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "AWS"
        AZURE = "Azure"
        AZURE_DEV_OPS = "AzureDevOps"
        DOCKER_HUB = "DockerHub"
        GCP = "GCP"
        GITHUB = "Github"
        GIT_LAB = "GitLab"
        J_FROG = "JFrog"


    class azure.mgmt.security.models.CloudOffering(Model):
        description: str
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Code(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.security.models.Compliance(Resource):
        assessment_result: list[ComplianceSegment]
        assessment_timestamp_utc_date: datetime
        id: str
        name: str
        resource_count: int
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ComplianceList(Model):
        next_link: str
        value: list[Compliance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Compliance]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ComplianceResult(Resource):
        id: str
        name: str
        resource_status: Union[str, ResourceStatus]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ComplianceResultList(Model):
        next_link: str
        value: list[ComplianceResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[ComplianceResult], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ComplianceSegment(Model):
        percentage: float
        segment_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Components1Uu4J47SchemasSecurityassessmentpropertiesbasePropertiesRiskPropertiesPathsItemsPropertiesEdgesItems(Model):
        id: str
        source_id: str
        target_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
                source_id: str, 
                target_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Condition(Model):
        operator: Union[str, GovernanceRuleConditionOperator]
        property: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operator: Optional[Union[str, GovernanceRuleConditionOperator]] = ..., 
                property: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ConnectableResource(Model):
        id: str
        inbound_connected_resources: list[ConnectedResource]
        outbound_connected_resources: list[ConnectedResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ConnectedResource(Model):
        connected_resource_id: str
        tcp_ports: str
        udp_ports: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ConnectedWorkspace(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ConnectionFromIpNotAllowed(AllowlistCustomAlertRule):
        allowlist_values: list[str]
        description: str
        display_name: str
        is_enabled: bool
        rule_type: str
        value_type: Union[str, ValueType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowlist_values: List[str], 
                is_enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ConnectionToIpNotAllowed(AllowlistCustomAlertRule):
        allowlist_values: list[str]
        description: str
        display_name: str
        is_enabled: bool
        rule_type: str
        value_type: Union[str, ValueType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowlist_values: List[str], 
                is_enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        INTERNAL = "Internal"


    class azure.mgmt.security.models.ConnectorSetting(Resource):
        authentication_details: AuthenticationDetailsProperties
        hybrid_compute_settings: HybridComputeSettingsProperties
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authentication_details: Optional[AuthenticationDetailsProperties] = ..., 
                hybrid_compute_settings: Optional[HybridComputeSettingsProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ConnectorSettingList(Model):
        next_link: str
        value: list[ConnectorSetting]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ConnectorSetting]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ContainerRegistryVulnerabilityProperties(AdditionalData):
        assessed_resource_type: Union[str, AssessedResourceType]
        cve: list[azure.mgmt.security.models.CVE]
        cvss: dict[str, azure.mgmt.security.models.CVSS]
        image_digest: str
        patchable: bool
        published_time: datetime
        repository_name: str
        type: str
        vendor_references: list[VendorReference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ControlType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN = "BuiltIn"
        CUSTOM = "Custom"


    class azure.mgmt.security.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.security.models.CspmMonitorAwsOffering(CloudOffering):
        description: str
        native_cloud_connection: CspmMonitorAwsOfferingNativeCloudConnection
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                native_cloud_connection: Optional[CspmMonitorAwsOfferingNativeCloudConnection] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CspmMonitorAwsOfferingNativeCloudConnection(Model):
        cloud_role_arn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CspmMonitorAzureDevOpsOffering(CloudOffering):
        description: str
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CspmMonitorDockerHubOffering(CloudOffering):
        description: str
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CspmMonitorGcpOffering(CloudOffering):
        description: str
        native_cloud_connection: CspmMonitorGcpOfferingNativeCloudConnection
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                native_cloud_connection: Optional[CspmMonitorGcpOfferingNativeCloudConnection] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CspmMonitorGcpOfferingNativeCloudConnection(Model):
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CspmMonitorGitLabOffering(CloudOffering):
        description: str
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CspmMonitorGithubOffering(CloudOffering):
        description: str
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CspmMonitorJFrogOffering(CloudOffering):
        description: str
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CustomAlertRule(Model):
        description: str
        display_name: str
        is_enabled: bool
        rule_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CustomAssessmentAutomation(Resource):
        assessment_key: str
        compressed_query: str
        description: str
        display_name: str
        id: str
        name: str
        remediation_description: str
        severity: Union[str, SeverityEnum]
        supported_cloud: Union[str, SupportedCloudEnum]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_key: Optional[str] = ..., 
                compressed_query: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                remediation_description: Optional[str] = ..., 
                severity: Union[str, SeverityEnum] = "Low", 
                supported_cloud: Union[str, SupportedCloudEnum] = "AWS", 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CustomAssessmentAutomationRequest(Resource):
        compressed_query: str
        description: str
        display_name: str
        id: str
        name: str
        remediation_description: str
        severity: Union[str, SeverityEnum]
        supported_cloud: Union[str, SupportedCloudEnum]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compressed_query: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                remediation_description: Optional[str] = ..., 
                severity: Union[str, SeverityEnum] = "Low", 
                supported_cloud: Union[str, SupportedCloudEnum] = "AWS", 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CustomAssessmentAutomationsListResult(Model):
        next_link: str
        value: list[CustomAssessmentAutomation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CustomEntityStoreAssignment(Resource):
        entity_store_database_link: str
        id: str
        name: str
        principal: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                entity_store_database_link: Optional[str] = ..., 
                principal: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CustomEntityStoreAssignmentRequest(Model):
        principal: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CustomEntityStoreAssignmentsListResult(Model):
        next_link: str
        value: list[CustomEntityStoreAssignment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CustomRecommendation(Resource):
        assessment_key: str
        cloud_providers: Union[list[str, RecommendationSupportedClouds]]
        description: str
        display_name: str
        id: str
        name: str
        query: str
        remediation_description: str
        security_issue: Union[str, SecurityIssue]
        severity: Union[str, SeverityEnum]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_providers: Optional[List[Union[str, RecommendationSupportedClouds]]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                query: Optional[str] = ..., 
                remediation_description: Optional[str] = ..., 
                security_issue: Union[str, SecurityIssue] = "BestPractices", 
                severity: Union[str, SeverityEnum] = "Low", 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.CustomRecommendationsList(Model):
        next_link: str
        value: list[CustomRecommendation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DataExportSettings(Setting):
        enabled: bool
        id: str
        kind: Union[str, SettingKind]
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DataSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TWIN_DATA = "TwinData"


    class azure.mgmt.security.models.DefenderCspmAwsOffering(CloudOffering):
        ciem: DefenderCspmAwsOfferingCiem
        data_sensitivity_discovery: DefenderCspmAwsOfferingDataSensitivityDiscovery
        databases_dspm: DefenderCspmAwsOfferingDatabasesDspm
        description: str
        mdc_containers_agentless_discovery_k8_s: DefenderCspmAwsOfferingMdcContainersAgentlessDiscoveryK8S
        mdc_containers_image_assessment: DefenderCspmAwsOfferingMdcContainersImageAssessment
        offering_type: Union[str, OfferingType]
        vm_scanners: DefenderCspmAwsOfferingVmScanners

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ciem: Optional[DefenderCspmAwsOfferingCiem] = ..., 
                data_sensitivity_discovery: Optional[DefenderCspmAwsOfferingDataSensitivityDiscovery] = ..., 
                databases_dspm: Optional[DefenderCspmAwsOfferingDatabasesDspm] = ..., 
                mdc_containers_agentless_discovery_k8_s: Optional[DefenderCspmAwsOfferingMdcContainersAgentlessDiscoveryK8S] = ..., 
                mdc_containers_image_assessment: Optional[DefenderCspmAwsOfferingMdcContainersImageAssessment] = ..., 
                vm_scanners: Optional[DefenderCspmAwsOfferingVmScanners] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingCiem(Model):
        ciem_discovery: DefenderCspmAwsOfferingCiemDiscovery
        ciem_oidc: DefenderCspmAwsOfferingCiemOidc

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ciem_discovery: Optional[DefenderCspmAwsOfferingCiemDiscovery] = ..., 
                ciem_oidc: Optional[DefenderCspmAwsOfferingCiemOidc] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingCiemDiscovery(Model):
        cloud_role_arn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingCiemOidc(Model):
        azure_active_directory_app_name: str
        cloud_role_arn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_active_directory_app_name: Optional[str] = ..., 
                cloud_role_arn: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingDataSensitivityDiscovery(Model):
        cloud_role_arn: str
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingDatabasesDspm(Model):
        cloud_role_arn: str
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingMdcContainersAgentlessDiscoveryK8S(Model):
        cloud_role_arn: str
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingMdcContainersImageAssessment(Model):
        cloud_role_arn: str
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingVmScanners(VmScannersAws):
        cloud_role_arn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmDockerHubOffering(CloudOffering):
        description: str
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmGcpOffering(CloudOffering):
        ciem_discovery: DefenderCspmGcpOfferingCiemDiscovery
        data_sensitivity_discovery: DefenderCspmGcpOfferingDataSensitivityDiscovery
        description: str
        mdc_containers_agentless_discovery_k8_s: DefenderCspmGcpOfferingMdcContainersAgentlessDiscoveryK8S
        mdc_containers_image_assessment: DefenderCspmGcpOfferingMdcContainersImageAssessment
        offering_type: Union[str, OfferingType]
        vm_scanners: DefenderCspmGcpOfferingVmScanners

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ciem_discovery: Optional[DefenderCspmGcpOfferingCiemDiscovery] = ..., 
                data_sensitivity_discovery: Optional[DefenderCspmGcpOfferingDataSensitivityDiscovery] = ..., 
                mdc_containers_agentless_discovery_k8_s: Optional[DefenderCspmGcpOfferingMdcContainersAgentlessDiscoveryK8S] = ..., 
                mdc_containers_image_assessment: Optional[DefenderCspmGcpOfferingMdcContainersImageAssessment] = ..., 
                vm_scanners: Optional[DefenderCspmGcpOfferingVmScanners] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingCiemDiscovery(Model):
        azure_active_directory_app_name: str
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_active_directory_app_name: Optional[str] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingDataSensitivityDiscovery(Model):
        enabled: bool
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingMdcContainersAgentlessDiscoveryK8S(Model):
        enabled: bool
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingMdcContainersImageAssessment(Model):
        enabled: bool
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingVmScanners(VmScannersGcp):
        configuration: VmScannersBaseConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmJFrogOffering(CloudOffering):
        description: str
        mdc_containers_image_assessment: DefenderCspmJFrogOfferingMdcContainersImageAssessment
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                mdc_containers_image_assessment: Optional[DefenderCspmJFrogOfferingMdcContainersImageAssessment] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderCspmJFrogOfferingMdcContainersImageAssessment(Model):
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderFoDatabasesAwsOffering(CloudOffering):
        arc_auto_provisioning: DefenderFoDatabasesAwsOfferingArcAutoProvisioning
        databases_dspm: DefenderFoDatabasesAwsOfferingDatabasesDspm
        description: str
        offering_type: Union[str, OfferingType]
        rds: DefenderFoDatabasesAwsOfferingRds

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arc_auto_provisioning: Optional[DefenderFoDatabasesAwsOfferingArcAutoProvisioning] = ..., 
                databases_dspm: Optional[DefenderFoDatabasesAwsOfferingDatabasesDspm] = ..., 
                rds: Optional[DefenderFoDatabasesAwsOfferingRds] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderFoDatabasesAwsOfferingArcAutoProvisioning(ArcAutoProvisioningAws):
        cloud_role_arn: str
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderFoDatabasesAwsOfferingDatabasesDspm(Model):
        cloud_role_arn: str
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderFoDatabasesAwsOfferingRds(Model):
        cloud_role_arn: str
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOffering(CloudOffering):
        cloud_watch_to_kinesis: DefenderForContainersAwsOfferingCloudWatchToKinesis
        data_collection_external_id: str
        description: str
        enable_audit_logs_auto_provisioning: bool
        enable_defender_agent_auto_provisioning: bool
        enable_policy_agent_auto_provisioning: bool
        kinesis_to_s3: DefenderForContainersAwsOfferingKinesisToS3
        kube_audit_retention_time: int
        kubernetes_data_collection: DefenderForContainersAwsOfferingKubernetesDataCollection
        kubernetes_service: DefenderForContainersAwsOfferingKubernetesService
        mdc_containers_agentless_discovery_k8_s: DefenderForContainersAwsOfferingMdcContainersAgentlessDiscoveryK8S
        mdc_containers_image_assessment: DefenderForContainersAwsOfferingMdcContainersImageAssessment
        offering_type: Union[str, OfferingType]
        vm_scanners: DefenderForContainersAwsOfferingVmScanners

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_watch_to_kinesis: Optional[DefenderForContainersAwsOfferingCloudWatchToKinesis] = ..., 
                data_collection_external_id: Optional[str] = ..., 
                enable_audit_logs_auto_provisioning: Optional[bool] = ..., 
                enable_defender_agent_auto_provisioning: Optional[bool] = ..., 
                enable_policy_agent_auto_provisioning: Optional[bool] = ..., 
                kinesis_to_s3: Optional[DefenderForContainersAwsOfferingKinesisToS3] = ..., 
                kube_audit_retention_time: Optional[int] = ..., 
                kubernetes_data_collection: Optional[DefenderForContainersAwsOfferingKubernetesDataCollection] = ..., 
                kubernetes_service: Optional[DefenderForContainersAwsOfferingKubernetesService] = ..., 
                mdc_containers_agentless_discovery_k8_s: Optional[DefenderForContainersAwsOfferingMdcContainersAgentlessDiscoveryK8S] = ..., 
                mdc_containers_image_assessment: Optional[DefenderForContainersAwsOfferingMdcContainersImageAssessment] = ..., 
                vm_scanners: Optional[DefenderForContainersAwsOfferingVmScanners] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingCloudWatchToKinesis(Model):
        cloud_role_arn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingKinesisToS3(Model):
        cloud_role_arn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingKubernetesDataCollection(Model):
        cloud_role_arn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingKubernetesService(Model):
        cloud_role_arn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingMdcContainersAgentlessDiscoveryK8S(Model):
        cloud_role_arn: str
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingMdcContainersImageAssessment(Model):
        cloud_role_arn: str
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingVmScanners(VmScannersAws):
        cloud_role_arn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersDockerHubOffering(CloudOffering):
        description: str
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOffering(CloudOffering):
        data_pipeline_native_cloud_connection: DefenderForContainersGcpOfferingDataPipelineNativeCloudConnection
        description: str
        enable_audit_logs_auto_provisioning: bool
        enable_defender_agent_auto_provisioning: bool
        enable_policy_agent_auto_provisioning: bool
        mdc_containers_agentless_discovery_k8_s: DefenderForContainersGcpOfferingMdcContainersAgentlessDiscoveryK8S
        mdc_containers_image_assessment: DefenderForContainersGcpOfferingMdcContainersImageAssessment
        native_cloud_connection: DefenderForContainersGcpOfferingNativeCloudConnection
        offering_type: Union[str, OfferingType]
        vm_scanners: DefenderForContainersGcpOfferingVmScanners

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_pipeline_native_cloud_connection: Optional[DefenderForContainersGcpOfferingDataPipelineNativeCloudConnection] = ..., 
                enable_audit_logs_auto_provisioning: Optional[bool] = ..., 
                enable_defender_agent_auto_provisioning: Optional[bool] = ..., 
                enable_policy_agent_auto_provisioning: Optional[bool] = ..., 
                mdc_containers_agentless_discovery_k8_s: Optional[DefenderForContainersGcpOfferingMdcContainersAgentlessDiscoveryK8S] = ..., 
                mdc_containers_image_assessment: Optional[DefenderForContainersGcpOfferingMdcContainersImageAssessment] = ..., 
                native_cloud_connection: Optional[DefenderForContainersGcpOfferingNativeCloudConnection] = ..., 
                vm_scanners: Optional[DefenderForContainersGcpOfferingVmScanners] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOfferingDataPipelineNativeCloudConnection(Model):
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOfferingMdcContainersAgentlessDiscoveryK8S(Model):
        enabled: bool
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOfferingMdcContainersImageAssessment(Model):
        enabled: bool
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOfferingNativeCloudConnection(Model):
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOfferingVmScanners(VmScannersGcp):
        configuration: VmScannersBaseConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForContainersJFrogOffering(CloudOffering):
        description: str
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForDatabasesGcpOffering(CloudOffering):
        arc_auto_provisioning: DefenderForDatabasesGcpOfferingArcAutoProvisioning
        defender_for_databases_arc_auto_provisioning: DefenderForDatabasesGcpOfferingDefenderForDatabasesArcAutoProvisioning
        description: str
        offering_type: Union[str, OfferingType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arc_auto_provisioning: Optional[DefenderForDatabasesGcpOfferingArcAutoProvisioning] = ..., 
                defender_for_databases_arc_auto_provisioning: Optional[DefenderForDatabasesGcpOfferingDefenderForDatabasesArcAutoProvisioning] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForDatabasesGcpOfferingArcAutoProvisioning(ArcAutoProvisioningGcp):
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForDatabasesGcpOfferingDefenderForDatabasesArcAutoProvisioning(Model):
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersAwsOffering(CloudOffering):
        arc_auto_provisioning: DefenderForServersAwsOfferingArcAutoProvisioning
        defender_for_servers: DefenderForServersAwsOfferingDefenderForServers
        description: str
        mde_auto_provisioning: DefenderForServersAwsOfferingMdeAutoProvisioning
        offering_type: Union[str, OfferingType]
        sub_plan: DefenderForServersAwsOfferingSubPlan
        va_auto_provisioning: DefenderForServersAwsOfferingVaAutoProvisioning
        vm_scanners: DefenderForServersAwsOfferingVmScanners

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arc_auto_provisioning: Optional[DefenderForServersAwsOfferingArcAutoProvisioning] = ..., 
                defender_for_servers: Optional[DefenderForServersAwsOfferingDefenderForServers] = ..., 
                mde_auto_provisioning: Optional[DefenderForServersAwsOfferingMdeAutoProvisioning] = ..., 
                sub_plan: Optional[DefenderForServersAwsOfferingSubPlan] = ..., 
                va_auto_provisioning: Optional[DefenderForServersAwsOfferingVaAutoProvisioning] = ..., 
                vm_scanners: Optional[DefenderForServersAwsOfferingVmScanners] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingArcAutoProvisioning(ArcAutoProvisioningAws):
        cloud_role_arn: str
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingDefenderForServers(Model):
        cloud_role_arn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingMdeAutoProvisioning(Model):
        configuration: JSON
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[JSON] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingSubPlan(Model):
        type: Union[str, SubPlan]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, SubPlan]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingVaAutoProvisioning(Model):
        configuration: DefenderForServersAwsOfferingVaAutoProvisioningConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[DefenderForServersAwsOfferingVaAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingVaAutoProvisioningConfiguration(Model):
        type: Union[str, Type]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, Type]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingVmScanners(VmScannersAws):
        cloud_role_arn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersGcpOffering(CloudOffering):
        arc_auto_provisioning: DefenderForServersGcpOfferingArcAutoProvisioning
        defender_for_servers: DefenderForServersGcpOfferingDefenderForServers
        description: str
        mde_auto_provisioning: DefenderForServersGcpOfferingMdeAutoProvisioning
        offering_type: Union[str, OfferingType]
        sub_plan: DefenderForServersGcpOfferingSubPlan
        va_auto_provisioning: DefenderForServersGcpOfferingVaAutoProvisioning
        vm_scanners: DefenderForServersGcpOfferingVmScanners

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arc_auto_provisioning: Optional[DefenderForServersGcpOfferingArcAutoProvisioning] = ..., 
                defender_for_servers: Optional[DefenderForServersGcpOfferingDefenderForServers] = ..., 
                mde_auto_provisioning: Optional[DefenderForServersGcpOfferingMdeAutoProvisioning] = ..., 
                sub_plan: Optional[DefenderForServersGcpOfferingSubPlan] = ..., 
                va_auto_provisioning: Optional[DefenderForServersGcpOfferingVaAutoProvisioning] = ..., 
                vm_scanners: Optional[DefenderForServersGcpOfferingVmScanners] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingArcAutoProvisioning(ArcAutoProvisioningGcp):
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingDefenderForServers(Model):
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingMdeAutoProvisioning(Model):
        configuration: JSON
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[JSON] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingSubPlan(Model):
        type: Union[str, SubPlan]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, SubPlan]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingVaAutoProvisioning(Model):
        configuration: DefenderForServersGcpOfferingVaAutoProvisioningConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[DefenderForServersGcpOfferingVaAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingVaAutoProvisioningConfiguration(Model):
        type: Union[str, Type]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, Type]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingVmScanners(VmScannersGcp):
        configuration: VmScannersBaseConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForStorageSetting(Resource):
        id: str
        name: str
        properties: DefenderForStorageSettingProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DefenderForStorageSettingProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DefenderForStorageSettingProperties(Model):
        is_enabled: bool
        malware_scanning: MalwareScanningProperties
        override_subscription_level_settings: bool
        sensitive_data_discovery: SensitiveDataDiscoveryProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ..., 
                malware_scanning: Optional[MalwareScanningProperties] = ..., 
                override_subscription_level_settings: Optional[bool] = ..., 
                sensitive_data_discovery: Optional[SensitiveDataDiscoveryProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DenylistCustomAlertRule(ListCustomAlertRule):
        denylist_values: list[str]
        description: str
        display_name: str
        is_enabled: bool
        rule_type: str
        value_type: Union[str, ValueType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                denylist_values: List[str], 
                is_enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DesiredOnboardingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.DevOpsCapability(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DevOpsConfiguration(ProxyResource):
        id: str
        name: str
        properties: DevOpsConfigurationProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DevOpsConfigurationProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DevOpsConfigurationListResponse(Model):
        next_link: str
        value: list[DevOpsConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DevOpsConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DevOpsConfigurationProperties(Model):
        agentless_configuration: AgentlessConfiguration
        authorization: Authorization
        auto_discovery: Union[str, AutoDiscovery]
        capabilities: list[DevOpsCapability]
        provisioning_state: Union[str, DevOpsProvisioningState]
        provisioning_status_message: str
        provisioning_status_update_time_utc: datetime
        top_level_inventory_list: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agentless_configuration: Optional[AgentlessConfiguration] = ..., 
                authorization: Optional[Authorization] = ..., 
                auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                top_level_inventory_list: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DevOpsProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETION_FAILURE = "DeletionFailure"
        DELETION_SUCCESS = "DeletionSuccess"
        FAILED = "Failed"
        PENDING = "Pending"
        PENDING_DELETION = "PendingDeletion"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.security.models.DeviceSecurityGroup(Resource):
        allowlist_rules: list[AllowlistCustomAlertRule]
        denylist_rules: list[DenylistCustomAlertRule]
        id: str
        name: str
        threshold_rules: list[ThresholdCustomAlertRule]
        time_window_rules: list[TimeWindowCustomAlertRule]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowlist_rules: Optional[List[AllowlistCustomAlertRule]] = ..., 
                denylist_rules: Optional[List[DenylistCustomAlertRule]] = ..., 
                threshold_rules: Optional[List[ThresholdCustomAlertRule]] = ..., 
                time_window_rules: Optional[List[TimeWindowCustomAlertRule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DeviceSecurityGroupList(Model):
        next_link: str
        value: list[DeviceSecurityGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DeviceSecurityGroup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DirectMethodInvokesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DiscoveredSecuritySolution(Resource, Location):
        id: str
        location: str
        name: str
        offer: str
        publisher: str
        security_family: Union[str, SecurityFamily]
        sku: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                offer: str, 
                publisher: str, 
                security_family: Union[str, SecurityFamily], 
                sku: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DiscoveredSecuritySolutionList(Model):
        next_link: str
        value: list[DiscoveredSecuritySolution]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DiscoveredSecuritySolution]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.DockerHubEnvironmentData(EnvironmentData):
        authentication: Authentication
        environment_type: Union[str, EnvironmentType]
        scan_interval: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authentication: Optional[Authentication] = ..., 
                scan_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ETag(Model):
        etag: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.EdgeIdentifiers(Model):
        source: str
        target: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source: str, 
                target: str, 
                type: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Effect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTEST = "Attest"
        AUDIT = "Audit"
        EXEMPT = "Exempt"


    class azure.mgmt.security.models.EndOfSupportStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        NO_LONGER_SUPPORTED = "noLongerSupported"
        UPCOMING_NO_LONGER_SUPPORTED = "upcomingNoLongerSupported"
        UPCOMING_VERSION_NO_LONGER_SUPPORTED = "upcomingVersionNoLongerSupported"
        VERSION_NO_LONGER_SUPPORTED = "versionNoLongerSupported"


    class azure.mgmt.security.models.Enforce(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.security.models.EnvironmentData(Model):
        environment_type: Union[str, EnvironmentType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.EnvironmentDetails(Model):
        environment_hierarchy_id: str
        native_resource_id: str
        organizational_hierarchy_id: str
        subscription_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                environment_hierarchy_id: Optional[str] = ..., 
                native_resource_id: Optional[str] = ..., 
                organizational_hierarchy_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.EnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS_ACCOUNT = "AwsAccount"
        AZURE_DEV_OPS_SCOPE = "AzureDevOpsScope"
        DOCKER_HUB_ORGANIZATION = "DockerHubOrganization"
        GCP_PROJECT = "GcpProject"
        GITHUB_SCOPE = "GithubScope"
        GITLAB_SCOPE = "GitlabScope"
        J_FROG_ARTIFACTORY = "JFrogArtifactory"


    class azure.mgmt.security.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ErrorDetailAutoGenerated(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetailAutoGenerated]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ErrorDetailAutoGenerated2(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetailAutoGenerated2]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ErrorResponseAutoGenerated(Model):
        error: ErrorDetailAutoGenerated

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetailAutoGenerated] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ErrorResponseAutoGenerated2(Model):
        error: ErrorDetailAutoGenerated2

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetailAutoGenerated2] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.EventSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"
        ASSESSMENTS = "Assessments"
        ASSESSMENTS_SNAPSHOT = "AssessmentsSnapshot"
        ATTACK_PATHS = "AttackPaths"
        ATTACK_PATHS_SNAPSHOT = "AttackPathsSnapshot"
        REGULATORY_COMPLIANCE_ASSESSMENT = "RegulatoryComplianceAssessment"
        REGULATORY_COMPLIANCE_ASSESSMENT_SNAPSHOT = "RegulatoryComplianceAssessmentSnapshot"
        SECURE_SCORES = "SecureScores"
        SECURE_SCORES_SNAPSHOT = "SecureScoresSnapshot"
        SECURE_SCORE_CONTROLS = "SecureScoreControls"
        SECURE_SCORE_CONTROLS_SNAPSHOT = "SecureScoreControlsSnapshot"
        SUB_ASSESSMENTS = "SubAssessments"
        SUB_ASSESSMENTS_SNAPSHOT = "SubAssessmentsSnapshot"


    class azure.mgmt.security.models.ExecuteGovernanceRuleParams(Model):
        override: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                override: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ExemptionCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MITIGATED = "mitigated"
        WAIVER = "waiver"


    class azure.mgmt.security.models.ExpandControlsEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFINITION = "definition"


    class azure.mgmt.security.models.ExpandEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINKS = "links"
        METADATA = "metadata"


    class azure.mgmt.security.models.ExportData(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RAW_EVENTS = "RawEvents"


    class azure.mgmt.security.models.Extension(Model):
        additional_extension_properties: dict[str, any]
        is_enabled: Union[str, IsEnabled]
        name: str
        operation_status: OperationStatusAutoGenerated

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_extension_properties: Optional[Dict[str, Any]] = ..., 
                is_enabled: Union[str, IsEnabled], 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ExternalSecuritySolution(Resource, ExternalSecuritySolutionKind, Location):
        id: str
        kind: Union[str, ExternalSecuritySolutionKindEnum]
        location: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ExternalSecuritySolutionKindEnum]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ExternalSecuritySolutionKind(Model):
        kind: Union[str, ExternalSecuritySolutionKindEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ExternalSecuritySolutionKindEnum]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ExternalSecuritySolutionKindEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "AAD"
        ATA = "ATA"
        CEF = "CEF"


    class azure.mgmt.security.models.ExternalSecuritySolutionList(Model):
        next_link: str
        value: list[ExternalSecuritySolution]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ExternalSecuritySolution]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ExternalSecuritySolutionProperties(Model):
        additional_properties: dict[str, any]
        device_type: str
        device_vendor: str
        workspace: ConnectedWorkspace

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                device_type: Optional[str] = ..., 
                device_vendor: Optional[str] = ..., 
                workspace: Optional[ConnectedWorkspace] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.FailedLocalLoginsNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.FileUploadsNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GcpCredentialsDetailsProperties(AuthenticationDetailsProperties):
        auth_provider_x509_cert_url: str
        auth_uri: str
        authentication_provisioning_state: Union[str, AuthenticationProvisioningState]
        authentication_type: Union[str, AuthenticationType]
        client_email: str
        client_id: str
        client_x509_cert_url: str
        granted_permissions: Union[list[str, PermissionProperty]]
        organization_id: str
        private_key: str
        private_key_id: str
        project_id: str
        token_uri: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_provider_x509_cert_url: str, 
                auth_uri: str, 
                client_email: str, 
                client_id: str, 
                client_x509_cert_url: str, 
                organization_id: str, 
                private_key: str, 
                private_key_id: str, 
                project_id: str, 
                token_uri: str, 
                type: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GcpOrganizationalData(Model):
        organization_membership_type: Union[str, OrganizationMembershipType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GcpOrganizationalDataMember(GcpOrganizationalData):
        management_project_number: str
        organization_membership_type: Union[str, OrganizationMembershipType]
        parent_hierarchy_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                management_project_number: Optional[str] = ..., 
                parent_hierarchy_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GcpOrganizationalDataOrganization(GcpOrganizationalData):
        excluded_project_numbers: list[str]
        organization_membership_type: Union[str, OrganizationMembershipType]
        organization_name: str
        service_account_email_address: str
        workload_identity_provider_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                excluded_project_numbers: Optional[List[str]] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GcpProjectDetails(Model):
        project_id: str
        project_name: str
        project_number: str
        workload_identity_pool_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                project_id: Optional[str] = ..., 
                project_number: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GcpProjectEnvironmentData(EnvironmentData):
        environment_type: Union[str, EnvironmentType]
        organizational_data: GcpOrganizationalData
        project_details: GcpProjectDetails
        scan_interval: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                organizational_data: Optional[GcpOrganizationalData] = ..., 
                project_details: Optional[GcpProjectDetails] = ..., 
                scan_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GetSensitivitySettingsListResponse(Model):
        value: list[GetSensitivitySettingsResponse]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[GetSensitivitySettingsResponse]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GetSensitivitySettingsResponse(Model):
        id: str
        name: str
        properties: GetSensitivitySettingsResponseProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[GetSensitivitySettingsResponseProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GetSensitivitySettingsResponseProperties(Model):
        mip_information: GetSensitivitySettingsResponsePropertiesMipInformation
        sensitive_info_types_ids: list[str]
        sensitivity_threshold_label_id: str
        sensitivity_threshold_label_order: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                mip_information: Optional[GetSensitivitySettingsResponsePropertiesMipInformation] = ..., 
                sensitive_info_types_ids: Optional[List[str]] = ..., 
                sensitivity_threshold_label_id: Optional[str] = ..., 
                sensitivity_threshold_label_order: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GetSensitivitySettingsResponsePropertiesMipInformation(Model):
        built_in_info_types: list[BuiltInInfoType]
        custom_info_types: list[InfoType]
        labels: list[Label]
        mip_integration_status: Union[str, MipIntegrationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                built_in_info_types: Optional[List[BuiltInInfoType]] = ..., 
                custom_info_types: Optional[List[InfoType]] = ..., 
                labels: Optional[List[Label]] = ..., 
                mip_integration_status: Optional[Union[str, MipIntegrationStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitHubOwner(ProxyResource):
        id: str
        name: str
        properties: GitHubOwnerProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[GitHubOwnerProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitHubOwnerConfiguration(Model):
        auto_discovery: Union[str, AutoDiscovery]
        repository_configs: dict[str, BaseResourceConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                repository_configs: Optional[Dict[str, BaseResourceConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitHubOwnerListResponse(Model):
        next_link: str
        value: list[GitHubOwner]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[GitHubOwner]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitHubOwnerProperties(Model):
        git_hub_internal_id: str
        onboarding_state: Union[str, OnboardingState]
        owner_url: str
        provisioning_state: Union[str, DevOpsProvisioningState]
        provisioning_status_message: str
        provisioning_status_update_time_utc: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                onboarding_state: Optional[Union[str, OnboardingState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitHubRepository(ProxyResource):
        id: str
        name: str
        properties: GitHubRepositoryProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[GitHubRepositoryProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitHubRepositoryListResponse(Model):
        next_link: str
        value: list[GitHubRepository]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[GitHubRepository]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitHubRepositoryProperties(Model):
        onboarding_state: Union[str, OnboardingState]
        parent_owner_name: str
        provisioning_state: Union[str, DevOpsProvisioningState]
        provisioning_status_message: str
        provisioning_status_update_time_utc: datetime
        repo_full_name: str
        repo_id: str
        repo_name: str
        repo_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                onboarding_state: Optional[Union[str, OnboardingState]] = ..., 
                parent_owner_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitLabGroup(ProxyResource):
        id: str
        name: str
        properties: GitLabGroupProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[GitLabGroupProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitLabGroupConfiguration(Model):
        auto_discovery: Union[str, AutoDiscovery]
        project_configs: dict[str, BaseResourceConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                project_configs: Optional[Dict[str, BaseResourceConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitLabGroupListResponse(Model):
        next_link: str
        value: list[GitLabGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[GitLabGroup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitLabGroupProperties(Model):
        fully_qualified_friendly_name: str
        fully_qualified_name: str
        onboarding_state: Union[str, OnboardingState]
        provisioning_state: Union[str, DevOpsProvisioningState]
        provisioning_status_message: str
        provisioning_status_update_time_utc: datetime
        url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                onboarding_state: Optional[Union[str, OnboardingState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitLabProject(ProxyResource):
        id: str
        name: str
        properties: GitLabProjectProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[GitLabProjectProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitLabProjectListResponse(Model):
        next_link: str
        value: list[GitLabProject]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[GitLabProject]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitLabProjectProperties(Model):
        fully_qualified_friendly_name: str
        fully_qualified_name: str
        fully_qualified_parent_group_name: str
        onboarding_state: Union[str, OnboardingState]
        provisioning_state: Union[str, DevOpsProvisioningState]
        provisioning_status_message: str
        provisioning_status_update_time_utc: datetime
        url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                onboarding_state: Optional[Union[str, OnboardingState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GithubScopeEnvironmentData(EnvironmentData):
        environment_type: Union[str, EnvironmentType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GitlabScopeEnvironmentData(EnvironmentData):
        environment_type: Union[str, EnvironmentType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GovernanceAssignment(Resource):
        additional_data: GovernanceAssignmentAdditionalData
        governance_email_notification: GovernanceEmailNotification
        id: str
        is_grace_period: bool
        name: str
        owner: str
        remediation_due_date: datetime
        remediation_eta: RemediationEta
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_data: Optional[GovernanceAssignmentAdditionalData] = ..., 
                governance_email_notification: Optional[GovernanceEmailNotification] = ..., 
                is_grace_period: Optional[bool] = ..., 
                owner: Optional[str] = ..., 
                remediation_due_date: Optional[datetime] = ..., 
                remediation_eta: Optional[RemediationEta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GovernanceAssignmentAdditionalData(Model):
        ticket_link: str
        ticket_number: int
        ticket_status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ticket_link: Optional[str] = ..., 
                ticket_number: Optional[int] = ..., 
                ticket_status: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GovernanceAssignmentsList(Model):
        next_link: str
        value: list[GovernanceAssignment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GovernanceEmailNotification(Model):
        disable_manager_email_notification: bool
        disable_owner_email_notification: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disable_manager_email_notification: Optional[bool] = ..., 
                disable_owner_email_notification: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GovernanceRule(Resource):
        condition_sets: list[JSON]
        description: str
        display_name: str
        excluded_scopes: list[str]
        governance_email_notification: GovernanceRuleEmailNotification
        id: str
        include_member_scopes: bool
        is_disabled: bool
        is_grace_period: bool
        metadata: GovernanceRuleMetadata
        name: str
        owner_source: GovernanceRuleOwnerSource
        remediation_timeframe: str
        rule_priority: int
        rule_type: Union[str, GovernanceRuleType]
        source_resource_type: Union[str, GovernanceRuleSourceResourceType]
        tenant_id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                condition_sets: Optional[List[JSON]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                excluded_scopes: Optional[List[str]] = ..., 
                governance_email_notification: Optional[GovernanceRuleEmailNotification] = ..., 
                include_member_scopes: Optional[bool] = ..., 
                is_disabled: Optional[bool] = ..., 
                is_grace_period: Optional[bool] = ..., 
                metadata: Optional[GovernanceRuleMetadata] = ..., 
                owner_source: Optional[GovernanceRuleOwnerSource] = ..., 
                remediation_timeframe: Optional[str] = ..., 
                rule_priority: Optional[int] = ..., 
                rule_type: Optional[Union[str, GovernanceRuleType]] = ..., 
                source_resource_type: Optional[Union[str, GovernanceRuleSourceResourceType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GovernanceRuleConditionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "Equals"
        IN = "In"
        IN_ENUM = "In"


    class azure.mgmt.security.models.GovernanceRuleEmailNotification(Model):
        disable_manager_email_notification: bool
        disable_owner_email_notification: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disable_manager_email_notification: Optional[bool] = ..., 
                disable_owner_email_notification: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GovernanceRuleList(Model):
        next_link: str
        value: list[GovernanceRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GovernanceRuleMetadata(Model):
        created_by: str
        created_on: datetime
        updated_by: str
        updated_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GovernanceRuleOwnerSource(Model):
        type: Union[str, GovernanceRuleOwnerSourceType]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, GovernanceRuleOwnerSourceType]] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.GovernanceRuleOwnerSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BY_TAG = "ByTag"
        MANUALLY = "Manually"


    class azure.mgmt.security.models.GovernanceRuleSourceResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSESSMENTS = "Assessments"


    class azure.mgmt.security.models.GovernanceRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTEGRATED = "Integrated"
        SERVICE_NOW = "ServiceNow"


    class azure.mgmt.security.models.HealthDataClassification(Model):
        component: str
        scenario: str
        scope: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                component: Optional[str] = ..., 
                scenario: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.HealthReport(Resource):
        affected_defenders_plans: list[str]
        affected_defenders_sub_plans: list[str]
        environment_details: EnvironmentDetails
        health_data_classification: HealthDataClassification
        id: str
        issues: list[Issue]
        name: str
        report_additional_data: dict[str, str]
        resource_details: ResourceDetailsAutoGenerated
        status: StatusAutoGenerated
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                affected_defenders_plans: Optional[List[str]] = ..., 
                affected_defenders_sub_plans: Optional[List[str]] = ..., 
                environment_details: Optional[EnvironmentDetails] = ..., 
                health_data_classification: Optional[HealthDataClassification] = ..., 
                issues: Optional[List[Issue]] = ..., 
                resource_details: Optional[ResourceDetailsAutoGenerated] = ..., 
                status: Optional[StatusAutoGenerated] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.HealthReportsList(Model):
        next_link: str
        value: list[HealthReport]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.HttpC2DMessagesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.HttpC2DRejectedMessagesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.HttpD2CMessagesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.HybridComputeProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPIRED = "Expired"
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.security.models.HybridComputeSettingsProperties(Model):
        auto_provision: Union[str, AutoProvision]
        hybrid_compute_provisioning_state: Union[str, HybridComputeProvisioningState]
        proxy_server: ProxyServerProperties
        region: str
        resource_group_name: str
        service_principal: ServicePrincipalProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_provision: Union[str, AutoProvision], 
                proxy_server: Optional[ProxyServerProperties] = ..., 
                region: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                service_principal: Optional[ServicePrincipalProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Literal[SystemAssigned]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ImplementationEffort(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MODERATE = "Moderate"


    class azure.mgmt.security.models.InfoType(Model):
        description: str
        id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.InformationProtectionKeyword(Model):
        can_be_numeric: bool
        custom: bool
        excluded: bool
        pattern: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                can_be_numeric: Optional[bool] = ..., 
                custom: Optional[bool] = ..., 
                excluded: Optional[bool] = ..., 
                pattern: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.InformationProtectionPolicy(Resource):
        id: str
        information_types: dict[str, InformationType]
        labels: dict[str, SensitivityLabel]
        last_modified_utc: datetime
        name: str
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                information_types: Optional[Dict[str, InformationType]] = ..., 
                labels: Optional[Dict[str, SensitivityLabel]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.InformationProtectionPolicyList(Model):
        next_link: str
        value: list[InformationProtectionPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[InformationProtectionPolicy]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.InformationProtectionPolicyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "custom"
        EFFECTIVE = "effective"


    class azure.mgmt.security.models.InformationType(Model):
        custom: bool
        description: str
        display_name: str
        enabled: bool
        keywords: list[InformationProtectionKeyword]
        order: int
        recommended_label_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                keywords: Optional[List[InformationProtectionKeyword]] = ..., 
                order: Optional[int] = ..., 
                recommended_label_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.InheritFromParentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.Inherited(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.security.models.Intent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLECTION = "Collection"
        COMMAND_AND_CONTROL = "CommandAndControl"
        CREDENTIAL_ACCESS = "CredentialAccess"
        DEFENSE_EVASION = "DefenseEvasion"
        DISCOVERY = "Discovery"
        EXECUTION = "Execution"
        EXFILTRATION = "Exfiltration"
        EXPLOITATION = "Exploitation"
        IMPACT = "Impact"
        INITIAL_ACCESS = "InitialAccess"
        LATERAL_MOVEMENT = "LateralMovement"
        PERSISTENCE = "Persistence"
        PRE_ATTACK = "PreAttack"
        PRIVILEGE_ESCALATION = "PrivilegeEscalation"
        PROBING = "Probing"
        UNKNOWN = "Unknown"


    class azure.mgmt.security.models.InventoryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DEV_OPS_ORGANIZATION = "AzureDevOpsOrganization"
        AZURE_DEV_OPS_PROJECT = "AzureDevOpsProject"
        AZURE_DEV_OPS_REPOSITORY = "AzureDevOpsRepository"
        GIT_HUB_OWNER = "GitHubOwner"
        GIT_HUB_REPOSITORY = "GitHubRepository"


    class azure.mgmt.security.models.InventoryList(Model):
        inventory_kind: Union[str, InventoryKind]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                inventory_kind: Optional[Union[str, InventoryKind]] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.InventoryListKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUSION = "Exclusion"
        INCLUSION = "Inclusion"


    class azure.mgmt.security.models.IoTSecurityAggregatedAlert(Resource, TagsResource):
        action_taken: str
        aggregated_date_utc: date
        alert_display_name: str
        alert_type: str
        count: int
        description: str
        effected_resource_type: str
        id: str
        log_analytics_query: str
        name: str
        remediation_steps: str
        reported_severity: Union[str, ReportedSeverity]
        system_source: str
        tags: dict[str, str]
        top_devices_list: list[IoTSecurityAggregatedAlertPropertiesTopDevicesListItem]
        type: str
        vendor_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecurityAggregatedAlertList(Model):
        next_link: str
        value: list[IoTSecurityAggregatedAlert]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[IoTSecurityAggregatedAlert], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecurityAggregatedAlertPropertiesTopDevicesListItem(Model):
        alerts_count: int
        device_id: str
        last_occurrence: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecurityAggregatedRecommendation(Resource, TagsResource):
        description: str
        detected_by: str
        healthy_devices: int
        id: str
        log_analytics_query: str
        name: str
        recommendation_display_name: str
        recommendation_name: str
        recommendation_type_id: str
        remediation_steps: str
        reported_severity: Union[str, ReportedSeverity]
        tags: dict[str, str]
        type: str
        unhealthy_device_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recommendation_name: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecurityAggregatedRecommendationList(Model):
        next_link: str
        value: list[IoTSecurityAggregatedRecommendation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[IoTSecurityAggregatedRecommendation], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecurityAlertedDevice(Model):
        alerts_count: int
        device_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecurityDeviceAlert(Model):
        alert_display_name: str
        alerts_count: int
        reported_severity: Union[str, ReportedSeverity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecurityDeviceRecommendation(Model):
        devices_count: int
        recommendation_display_name: str
        reported_severity: Union[str, ReportedSeverity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecuritySolutionAnalyticsModel(Resource):
        devices_metrics: list[IoTSecuritySolutionAnalyticsModelPropertiesDevicesMetricsItem]
        id: str
        metrics: IoTSeverityMetrics
        most_prevalent_device_alerts: list[IoTSecurityDeviceAlert]
        most_prevalent_device_recommendations: list[IoTSecurityDeviceRecommendation]
        name: str
        top_alerted_devices: list[IoTSecurityAlertedDevice]
        type: str
        unhealthy_device_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                most_prevalent_device_alerts: Optional[List[IoTSecurityDeviceAlert]] = ..., 
                most_prevalent_device_recommendations: Optional[List[IoTSecurityDeviceRecommendation]] = ..., 
                top_alerted_devices: Optional[List[IoTSecurityAlertedDevice]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecuritySolutionAnalyticsModelList(Model):
        next_link: str
        value: list[IoTSecuritySolutionAnalyticsModel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[IoTSecuritySolutionAnalyticsModel], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecuritySolutionAnalyticsModelPropertiesDevicesMetricsItem(Model):
        date: datetime
        devices_metrics: IoTSeverityMetrics

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                date: Optional[datetime] = ..., 
                devices_metrics: Optional[IoTSeverityMetrics] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecuritySolutionModel(Resource, TagsResource):
        additional_workspaces: list[AdditionalWorkspacesProperties]
        auto_discovered_resources: list[str]
        disabled_data_sources: Union[list[str, DataSource]]
        display_name: str
        export: Union[list[str, ExportData]]
        id: str
        iot_hubs: list[str]
        location: str
        name: str
        recommendations_configuration: list[RecommendationConfigurationProperties]
        status: Union[str, SecuritySolutionStatus]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        unmasked_ip_logging_status: Union[str, UnmaskedIpLoggingStatus]
        user_defined_resources: UserDefinedResourcesProperties
        workspace: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_workspaces: Optional[List[AdditionalWorkspacesProperties]] = ..., 
                disabled_data_sources: Optional[List[Union[str, DataSource]]] = ..., 
                display_name: Optional[str] = ..., 
                export: Optional[List[Union[str, ExportData]]] = ..., 
                iot_hubs: Optional[List[str]] = ..., 
                location: Optional[str] = ..., 
                recommendations_configuration: Optional[List[RecommendationConfigurationProperties]] = ..., 
                status: Union[str, SecuritySolutionStatus] = "Enabled", 
                tags: Optional[Dict[str, str]] = ..., 
                unmasked_ip_logging_status: Union[str, UnmaskedIpLoggingStatus] = "Disabled", 
                user_defined_resources: Optional[UserDefinedResourcesProperties] = ..., 
                workspace: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSecuritySolutionsList(Model):
        next_link: str
        value: list[IoTSecuritySolutionModel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[IoTSecuritySolutionModel], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IoTSeverityMetrics(Model):
        high: int
        low: int
        medium: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                high: Optional[int] = ..., 
                low: Optional[int] = ..., 
                medium: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.IsEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.security.models.Issue(Model):
        issue_additional_data: dict[str, str]
        issue_description: str
        issue_key: str
        issue_name: str
        remediation_script: str
        remediation_steps: str
        security_values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                issue_additional_data: Optional[Dict[str, str]] = ..., 
                issue_description: Optional[str] = ..., 
                issue_key: str, 
                issue_name: Optional[str] = ..., 
                remediation_script: Optional[str] = ..., 
                remediation_steps: Optional[str] = ..., 
                security_values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JFrogEnvironmentData(EnvironmentData):
        environment_type: Union[str, EnvironmentType]
        scan_interval: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scan_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JitNetworkAccessPoliciesList(Model):
        next_link: str
        value: list[JitNetworkAccessPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[JitNetworkAccessPolicy]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicy(Resource, Kind, Location):
        id: str
        kind: str
        location: str
        name: str
        provisioning_state: str
        requests: list[JitNetworkAccessRequest]
        type: str
        virtual_machines: list[JitNetworkAccessPolicyVirtualMachine]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                requests: Optional[List[JitNetworkAccessRequest]] = ..., 
                virtual_machines: List[JitNetworkAccessPolicyVirtualMachine], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicyInitiatePort(Model):
        allowed_source_address_prefix: str
        end_time_utc: datetime
        number: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_source_address_prefix: Optional[str] = ..., 
                end_time_utc: datetime, 
                number: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicyInitiateRequest(Model):
        justification: str
        virtual_machines: list[JitNetworkAccessPolicyInitiateVirtualMachine]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                justification: Optional[str] = ..., 
                virtual_machines: List[JitNetworkAccessPolicyInitiateVirtualMachine], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicyInitiateVirtualMachine(Model):
        id: str
        ports: list[JitNetworkAccessPolicyInitiatePort]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
                ports: List[JitNetworkAccessPolicyInitiatePort], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicyVirtualMachine(Model):
        id: str
        ports: list[JitNetworkAccessPortRule]
        public_ip_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
                ports: List[JitNetworkAccessPortRule], 
                public_ip_address: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JitNetworkAccessPortRule(Model):
        allowed_source_address_prefix: str
        allowed_source_address_prefixes: list[str]
        max_request_access_duration: str
        number: int
        protocol: Union[str, ProtocolEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_source_address_prefix: Optional[str] = ..., 
                allowed_source_address_prefixes: Optional[List[str]] = ..., 
                max_request_access_duration: str, 
                number: int, 
                protocol: Union[str, ProtocolEnum], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JitNetworkAccessRequest(Model):
        justification: str
        requestor: str
        start_time_utc: datetime
        virtual_machines: list[JitNetworkAccessRequestVirtualMachine]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                justification: Optional[str] = ..., 
                requestor: str, 
                start_time_utc: datetime, 
                virtual_machines: List[JitNetworkAccessRequestVirtualMachine], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JitNetworkAccessRequestPort(Model):
        allowed_source_address_prefix: str
        allowed_source_address_prefixes: list[str]
        end_time_utc: datetime
        mapped_port: int
        number: int
        status: Union[str, Status]
        status_reason: Union[str, StatusReason]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_source_address_prefix: Optional[str] = ..., 
                allowed_source_address_prefixes: Optional[List[str]] = ..., 
                end_time_utc: datetime, 
                mapped_port: Optional[int] = ..., 
                number: int, 
                status: Union[str, Status], 
                status_reason: Union[str, StatusReason], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.JitNetworkAccessRequestVirtualMachine(Model):
        id: str
        ports: list[JitNetworkAccessRequestPort]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
                ports: List[JitNetworkAccessRequestPort], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Kind(Model):
        kind: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.KindEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUNDLES = "Bundles"


    class azure.mgmt.security.models.Label(Model):
        id: str
        name: str
        order: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                order: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ListCustomAlertRule(CustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        rule_type: str
        value_type: Union[str, ValueType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.LocalUserNotAllowed(AllowlistCustomAlertRule):
        allowlist_values: list[str]
        description: str
        display_name: str
        is_enabled: bool
        rule_type: str
        value_type: Union[str, ValueType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowlist_values: List[str], 
                is_enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Location(Model):
        location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.LogAnalyticsIdentifier(ResourceIdentifier):
        agent_id: str
        type: Union[str, ResourceIdentifierType]
        workspace_id: str
        workspace_resource_group: str
        workspace_subscription_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.MalwareScan(Model):
        properties: MalwareScanProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[MalwareScanProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.MalwareScanProperties(Model):
        scan_end_time: str
        scan_id: str
        scan_start_time: str
        scan_status: str
        scan_status_message: str
        scan_summary: ScanSummary

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scan_end_time: Optional[str] = ..., 
                scan_id: Optional[str] = ..., 
                scan_start_time: Optional[str] = ..., 
                scan_status: Optional[str] = ..., 
                scan_status_message: Optional[str] = ..., 
                scan_summary: Optional[ScanSummary] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.MalwareScanningProperties(Model):
        blob_scan_results_options: Union[str, BlobScanResultsOptions]
        on_upload: OnUploadProperties
        operation_status: OperationStatus
        scan_results_event_grid_topic_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_scan_results_options: Optional[Union[str, BlobScanResultsOptions]] = ..., 
                on_upload: Optional[OnUploadProperties] = ..., 
                scan_results_event_grid_topic_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.MdeOnboardingData(Resource):
        id: str
        name: str
        onboarding_package_linux: bytes
        onboarding_package_windows: bytes
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                onboarding_package_linux: Optional[bytes] = ..., 
                onboarding_package_windows: Optional[bytes] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.MdeOnboardingDataList(Model):
        value: list[MdeOnboardingData]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[MdeOnboardingData]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.MinimalRiskLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.MinimalSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.MipIntegrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_AUTO_LABELING_RULES = "noAutoLabelingRules"
        NO_CONSENT = "noConsent"
        NO_MIP_LABELS = "noMipLabels"
        OK = "Ok"


    class azure.mgmt.security.models.MqttC2DMessagesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.MqttC2DRejectedMessagesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.MqttD2CMessagesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.NodeIdentifier(Model):
        id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
                type: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.NotificationsSource(Model):
        source_type: Union[str, SourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.NotificationsSourceAlert(NotificationsSource):
        minimal_severity: Union[str, MinimalSeverity]
        source_type: Union[str, SourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                minimal_severity: Optional[Union[str, MinimalSeverity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.NotificationsSourceAttackPath(NotificationsSource):
        minimal_risk_level: Union[str, MinimalRiskLevel]
        source_type: Union[str, SourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                minimal_risk_level: Optional[Union[str, MinimalRiskLevel]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OfferingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSPM_MONITOR_AWS = "CspmMonitorAws"
        CSPM_MONITOR_AZURE_DEV_OPS = "CspmMonitorAzureDevOps"
        CSPM_MONITOR_DOCKER_HUB = "CspmMonitorDockerHub"
        CSPM_MONITOR_GCP = "CspmMonitorGcp"
        CSPM_MONITOR_GITHUB = "CspmMonitorGithub"
        CSPM_MONITOR_GIT_LAB = "CspmMonitorGitLab"
        CSPM_MONITOR_J_FROG = "CspmMonitorJFrog"
        DEFENDER_CSPM_AWS = "DefenderCspmAws"
        DEFENDER_CSPM_DOCKER_HUB = "DefenderCspmDockerHub"
        DEFENDER_CSPM_GCP = "DefenderCspmGcp"
        DEFENDER_CSPM_J_FROG = "DefenderCspmJFrog"
        DEFENDER_FOR_CONTAINERS_AWS = "DefenderForContainersAws"
        DEFENDER_FOR_CONTAINERS_DOCKER_HUB = "DefenderForContainersDockerHub"
        DEFENDER_FOR_CONTAINERS_GCP = "DefenderForContainersGcp"
        DEFENDER_FOR_CONTAINERS_J_FROG = "DefenderForContainersJFrog"
        DEFENDER_FOR_DATABASES_AWS = "DefenderForDatabasesAws"
        DEFENDER_FOR_DATABASES_GCP = "DefenderForDatabasesGcp"
        DEFENDER_FOR_SERVERS_AWS = "DefenderForServersAws"
        DEFENDER_FOR_SERVERS_GCP = "DefenderForServersGcp"


    class azure.mgmt.security.models.OnPremiseResourceDetails(ResourceDetails):
        machine_name: str
        source: Union[str, Source]
        source_computer_id: str
        vmuuid: str
        workspace_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                machine_name: str, 
                source_computer_id: str, 
                vmuuid: str, 
                workspace_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OnPremiseSqlResourceDetails(OnPremiseResourceDetails):
        database_name: str
        machine_name: str
        server_name: str
        source: Union[str, Source]
        source_computer_id: str
        vmuuid: str
        workspace_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_name: str, 
                machine_name: str, 
                server_name: str, 
                source_computer_id: str, 
                vmuuid: str, 
                workspace_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OnUploadFilters(Model):
        exclude_blobs_larger_than: any
        exclude_blobs_with_prefix: list[str]
        exclude_blobs_with_suffix: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                exclude_blobs_larger_than: Optional[Any] = ..., 
                exclude_blobs_with_prefix: Optional[List[str]] = ..., 
                exclude_blobs_with_suffix: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OnUploadProperties(Model):
        cap_gb_per_month: int
        filters: OnUploadFilters
        is_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cap_gb_per_month: Optional[int] = ..., 
                filters: Optional[OnUploadFilters] = ..., 
                is_enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OnboardingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_APPLICABLE = "NotApplicable"
        NOT_ONBOARDED = "NotOnboarded"
        ONBOARDED = "Onboarded"
        ONBOARDED_BY_OTHER_CONNECTOR = "OnboardedByOtherConnector"


    class azure.mgmt.security.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OperationResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.security.models.OperationResultAutoGenerated(Model):
        status: Union[str, OperationResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OperationStatus(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OperationStatusAutoGenerated(Model):
        code: Union[str, Code]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[Union[str, Code]] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.OperationStatusResult(Model):
        end_time: datetime
        error: ErrorDetailAutoGenerated2
        id: str
        name: str
        operations: list[OperationStatusResult]
        percent_complete: float
        start_time: datetime
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetailAutoGenerated2] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[List[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUALS = "Equals"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL_TO = "GreaterThanOrEqualTo"
        LESSER_THAN = "LesserThan"
        LESSER_THAN_OR_EQUAL_TO = "LesserThanOrEqualTo"
        NOT_EQUALS = "NotEquals"
        STARTS_WITH = "StartsWith"


    class azure.mgmt.security.models.OrganizationMembershipType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEMBER = "Member"
        ORGANIZATION = "Organization"


    class azure.mgmt.security.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.security.models.PartialAssessmentProperties(Model):
        assessment_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Path(Model):
        edges: list[EdgeIdentifiers]
        id: str
        nodes: list[NodeIdentifier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                edges: List[EdgeIdentifiers], 
                id: str, 
                nodes: List[NodeIdentifier], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PermissionProperty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS_AMAZON_SSM_AUTOMATION_ROLE = "AWS::AmazonSSMAutomationRole"
        AWS_AWS_SECURITY_HUB_READ_ONLY_ACCESS = "AWS::AWSSecurityHubReadOnlyAccess"
        AWS_SECURITY_AUDIT = "AWS::SecurityAudit"
        GCP_SECURITY_CENTER_ADMIN_VIEWER = "GCP::Security Center Admin Viewer"


    class azure.mgmt.security.models.Pricing(Resource):
        deprecated: bool
        enablement_time: datetime
        enforce: Union[str, Enforce]
        extensions: list[Extension]
        free_trial_remaining_time: timedelta
        id: str
        inherited: Union[str, Inherited]
        inherited_from: str
        name: str
        pricing_tier: Union[str, PricingTier]
        replaced_by: list[str]
        resources_coverage_status: Union[str, ResourcesCoverageStatus]
        sub_plan: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enforce: Optional[Union[str, Enforce]] = ..., 
                extensions: Optional[List[Extension]] = ..., 
                pricing_tier: Optional[Union[str, PricingTier]] = ..., 
                sub_plan: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PricingList(Model):
        value: list[Pricing]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[Pricing], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PricingTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE = "Free"
        STANDARD = "Standard"


    class azure.mgmt.security.models.PrivateEndpoint(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PrivateEndpointConnection(ResourceAutoGenerated):
        group_ids: list[str]
        id: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PrivateEndpointConnectionListResult(Model):
        next_link: str
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateEndpointConnection]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.security.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.security.models.PrivateLinkParameters(Model):
        private_link_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_link_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PrivateLinkResource(TrackedResourceAutoGenerated):
        id: str
        location: str
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        private_link_resources: list[PrivateLinkResourceAutoGenerated]
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PrivateLinkResourceAutoGenerated(ResourceAutoGenerated):
        group_id: str
        id: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                required_zone_names: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PrivateLinkResourceListResult(Model):
        next_link: str
        value: list[PrivateLinkResourceAutoGenerated]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateLinkResourceAutoGenerated]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PrivateLinkUpdate(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PrivateLinksList(Model):
        next_link: str
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ProcessNotAllowed(AllowlistCustomAlertRule):
        allowlist_values: list[str]
        description: str
        display_name: str
        is_enabled: bool
        rule_type: str
        value_type: Union[str, ValueType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowlist_values: List[str], 
                is_enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.PropertyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "Boolean"
        INTEGER = "Integer"
        NUMBER = "Number"
        STRING = "String"


    class azure.mgmt.security.models.ProtocolEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "*"
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.security.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.security.models.ProxyResource(ResourceAutoGenerated3):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ProxyServerProperties(Model):
        ip: str
        port: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip: Optional[str] = ..., 
                port: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.QueryCheck(Model):
        column_names: list[str]
        expected_result: list[list[str]]
        query: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                column_names: Optional[List[str]] = ..., 
                expected_result: Optional[List[List[str]]] = ..., 
                query: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.QueuePurgesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Rank(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        NONE = "None"


    class azure.mgmt.security.models.RecommendationConfigStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.RecommendationConfigurationProperties(Model):
        name: str
        recommendation_type: Union[str, RecommendationType]
        status: Union[str, RecommendationConfigStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recommendation_type: Union[str, RecommendationType], 
                status: Union[str, RecommendationConfigStatus] = "Enabled", 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RecommendationSupportedClouds(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "AWS"
        AZURE = "Azure"
        GCP = "GCP"


    class azure.mgmt.security.models.RecommendationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IO_T_ACRAUTHENTICATION = "IoT_ACRAuthentication"
        IO_T_AGENT_SENDS_UNUTILIZED_MESSAGES = "IoT_AgentSendsUnutilizedMessages"
        IO_T_BASELINE = "IoT_Baseline"
        IO_T_EDGE_HUB_MEM_OPTIMIZE = "IoT_EdgeHubMemOptimize"
        IO_T_EDGE_LOGGING_OPTIONS = "IoT_EdgeLoggingOptions"
        IO_T_INCONSISTENT_MODULE_SETTINGS = "IoT_InconsistentModuleSettings"
        IO_T_INSTALL_AGENT = "IoT_InstallAgent"
        IO_T_IPFILTER_DENY_ALL = "IoT_IPFilter_DenyAll"
        IO_T_IPFILTER_PERMISSIVE_RULE = "IoT_IPFilter_PermissiveRule"
        IO_T_OPEN_PORTS = "IoT_OpenPorts"
        IO_T_PERMISSIVE_FIREWALL_POLICY = "IoT_PermissiveFirewallPolicy"
        IO_T_PERMISSIVE_INPUT_FIREWALL_RULES = "IoT_PermissiveInputFirewallRules"
        IO_T_PERMISSIVE_OUTPUT_FIREWALL_RULES = "IoT_PermissiveOutputFirewallRules"
        IO_T_PRIVILEGED_DOCKER_OPTIONS = "IoT_PrivilegedDockerOptions"
        IO_T_SHARED_CREDENTIALS = "IoT_SharedCredentials"
        IO_T_VULNERABLE_TLS_CIPHER_SUITE = "IoT_VulnerableTLSCipherSuite"


    class azure.mgmt.security.models.RegulatoryComplianceAssessment(Resource):
        assessment_details_link: str
        assessment_type: str
        description: str
        failed_resources: int
        id: str
        name: str
        passed_resources: int
        skipped_resources: int
        state: Union[str, State]
        type: str
        unsupported_resources: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                state: Optional[Union[str, State]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RegulatoryComplianceAssessmentList(Model):
        next_link: str
        value: list[RegulatoryComplianceAssessment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[RegulatoryComplianceAssessment], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RegulatoryComplianceControl(Resource):
        description: str
        failed_assessments: int
        id: str
        name: str
        passed_assessments: int
        skipped_assessments: int
        state: Union[str, State]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                state: Optional[Union[str, State]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RegulatoryComplianceControlList(Model):
        next_link: str
        value: list[RegulatoryComplianceControl]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[RegulatoryComplianceControl], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RegulatoryComplianceStandard(Resource):
        failed_controls: int
        id: str
        name: str
        passed_controls: int
        skipped_controls: int
        state: Union[str, State]
        type: str
        unsupported_controls: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                state: Optional[Union[str, State]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RegulatoryComplianceStandardList(Model):
        next_link: str
        value: list[RegulatoryComplianceStandard]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[RegulatoryComplianceStandard], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Remediation(Model):
        automated: bool
        description: str
        portal_link: str
        scripts: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                automated: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                portal_link: Optional[str] = ..., 
                scripts: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RemediationEta(Model):
        eta: datetime
        justification: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                eta: datetime, 
                justification: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ReportedSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        INFORMATIONAL = "Informational"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.Resource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ResourceAutoGenerated(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ResourceAutoGenerated2(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ResourceAutoGenerated3(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ResourceDetails(Model):
        source: Union[str, Source]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ResourceDetailsAutoGenerated(Model):
        connector_id: str
        id: str
        source: Union[str, Source]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source: Optional[Union[str, Source]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ResourceIdentifier(Model):
        type: Union[str, ResourceIdentifierType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ResourceIdentifierType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_RESOURCE = "AzureResource"
        LOG_ANALYTICS = "LogAnalytics"


    class azure.mgmt.security.models.ResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_APPLICABLE = "NotApplicable"
        NOT_HEALTHY = "NotHealthy"
        OFF_BY_POLICY = "OffByPolicy"


    class azure.mgmt.security.models.ResourcesCoverageStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULLY_COVERED = "FullyCovered"
        NOT_COVERED = "NotCovered"
        PARTIALLY_COVERED = "PartiallyCovered"


    class azure.mgmt.security.models.RiskLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.RuleCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARTIFACTS = "Artifacts"
        CODE = "Code"
        CONTAINERS = "Containers"
        DEPENDENCIES = "Dependencies"
        IA_C = "IaC"
        SECRETS = "Secrets"


    class azure.mgmt.security.models.RuleResults(Resource):
        id: str
        name: str
        properties: RuleResultsProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[RuleResultsProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RuleResultsInput(Model):
        latest_scan: bool
        results: list[list[str]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                latest_scan: Optional[bool] = ..., 
                results: Optional[List[List[str]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RuleResultsProperties(Model):
        results: list[list[str]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                results: Optional[List[List[str]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RuleSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        INFORMATIONAL = "Informational"
        LOW = "Low"
        MEDIUM = "Medium"
        OBSOLETE = "Obsolete"


    class azure.mgmt.security.models.RuleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        EXPIRED = "Expired"


    class azure.mgmt.security.models.RuleStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FINDING = "Finding"
        INTERNAL_ERROR = "InternalError"
        NON_FINDING = "NonFinding"


    class azure.mgmt.security.models.RuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASELINE_EXPECTED = "BaselineExpected"
        BINARY = "Binary"
        NEGATIVE_LIST = "NegativeList"
        POSITIVE_LIST = "PositiveList"


    class azure.mgmt.security.models.RulesResults(Model):
        value: list[RuleResults]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[RuleResults]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.RulesResultsInput(Model):
        latest_scan: bool
        results: dict[str, list[list[str]]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                latest_scan: Optional[bool] = ..., 
                results: Optional[Dict[str, List[List[str]]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Scan(Resource):
        id: str
        name: str
        properties: ScanProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ScanProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ScanProperties(Model):
        database: str
        end_time: datetime
        high_severity_failed_rules_count: int
        is_baseline_applied: bool
        last_scan_time: datetime
        low_severity_failed_rules_count: int
        medium_severity_failed_rules_count: int
        server: str
        sql_version: str
        start_time: datetime
        state: Union[str, ScanState]
        total_failed_rules_count: int
        total_passed_rules_count: int
        total_rules_count: int
        trigger_type: Union[str, ScanTriggerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                high_severity_failed_rules_count: Optional[int] = ..., 
                is_baseline_applied: Optional[bool] = ..., 
                last_scan_time: Optional[datetime] = ..., 
                low_severity_failed_rules_count: Optional[int] = ..., 
                medium_severity_failed_rules_count: Optional[int] = ..., 
                server: Optional[str] = ..., 
                sql_version: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                state: Optional[Union[str, ScanState]] = ..., 
                total_failed_rules_count: Optional[int] = ..., 
                total_passed_rules_count: Optional[int] = ..., 
                total_rules_count: Optional[int] = ..., 
                trigger_type: Optional[Union[str, ScanTriggerType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ScanResult(Resource):
        id: str
        name: str
        properties: ScanResultProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ScanResultProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ScanResultProperties(Model):
        baseline_adjusted_result: BaselineAdjustedResult
        is_trimmed: bool
        query_results: list[list[str]]
        remediation: Remediation
        rule_id: str
        rule_metadata: VaRule
        status: Union[str, RuleStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                baseline_adjusted_result: Optional[BaselineAdjustedResult] = ..., 
                is_trimmed: Optional[bool] = ..., 
                query_results: Optional[List[List[str]]] = ..., 
                remediation: Optional[Remediation] = ..., 
                rule_id: Optional[str] = ..., 
                rule_metadata: Optional[VaRule] = ..., 
                status: Optional[Union[str, RuleStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ScanResults(Model):
        value: list[ScanResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ScanResult]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ScanState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        FAILED_TO_RUN = "FailedToRun"
        IN_PROGRESS = "InProgress"
        PASSED = "Passed"


    class azure.mgmt.security.models.ScanSummary(Model):
        blobs: BlobsScanSummary
        estimated_scan_cost_usd: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blobs: Optional[BlobsScanSummary] = ..., 
                estimated_scan_cost_usd: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ScanTriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_DEMAND = "OnDemand"
        RECURRING = "Recurring"


    class azure.mgmt.security.models.ScanningMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"


    class azure.mgmt.security.models.Scans(Model):
        value: list[Scan]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Scan]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ScopeElement(Model):
        additional_properties: dict[str, any]
        field: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                field: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecureScoreControlDefinitionItem(Resource):
        assessment_definitions: list[AzureResourceLink]
        description: str
        display_name: str
        id: str
        max_score: int
        name: str
        source: SecureScoreControlDefinitionSource
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecureScoreControlDefinitionList(Model):
        next_link: str
        value: list[SecureScoreControlDefinitionItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecureScoreControlDefinitionSource(Model):
        source_type: Union[str, ControlType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_type: Optional[Union[str, ControlType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecureScoreControlDetails(Resource):
        current: float
        definition: SecureScoreControlDefinitionItem
        display_name: str
        healthy_resource_count: int
        id: str
        max: int
        name: str
        not_applicable_resource_count: int
        percentage: float
        type: str
        unhealthy_resource_count: int
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                definition: Optional[SecureScoreControlDefinitionItem] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecureScoreControlList(Model):
        next_link: str
        value: list[SecureScoreControlDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecureScoreControlScore(Model):
        current: float
        max: int
        percentage: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecureScoreItem(Resource):
        current: float
        display_name: str
        id: str
        max: int
        name: str
        percentage: float
        type: str
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecureScoresList(Model):
        next_link: str
        value: list[SecureScoreItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessment(Resource):
        additional_data: dict[str, str]
        display_name: str
        id: str
        links: AssessmentLinks
        metadata: SecurityAssessmentMetadataProperties
        name: str
        partners_data: SecurityAssessmentPartnerData
        resource_details: ResourceDetails
        risk: SecurityAssessmentPropertiesBaseRisk
        status: AssessmentStatus
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_data: Optional[Dict[str, str]] = ..., 
                metadata: Optional[SecurityAssessmentMetadataProperties] = ..., 
                partners_data: Optional[SecurityAssessmentPartnerData] = ..., 
                resource_details: Optional[ResourceDetails] = ..., 
                risk: Optional[SecurityAssessmentPropertiesBaseRisk] = ..., 
                status: Optional[AssessmentStatus] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentList(Model):
        next_link: str
        value: list[SecurityAssessmentResponse]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadata(Resource):
        assessment_type: Union[str, AssessmentType]
        categories: Union[list[str, Categories]]
        description: str
        display_name: str
        id: str
        implementation_effort: Union[str, ImplementationEffort]
        name: str
        partner_data: SecurityAssessmentMetadataPartnerData
        policy_definition_id: str
        preview: bool
        remediation_description: str
        severity: Union[str, Severity]
        threats: Union[list[str, Threats]]
        type: str
        user_impact: Union[str, UserImpact]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_type: Optional[Union[str, AssessmentType]] = ..., 
                categories: Optional[List[Union[str, Categories]]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                implementation_effort: Optional[Union[str, ImplementationEffort]] = ..., 
                partner_data: Optional[SecurityAssessmentMetadataPartnerData] = ..., 
                preview: Optional[bool] = ..., 
                remediation_description: Optional[str] = ..., 
                severity: Optional[Union[str, Severity]] = ..., 
                threats: Optional[List[Union[str, Threats]]] = ..., 
                user_impact: Optional[Union[str, UserImpact]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataPartnerData(Model):
        partner_name: str
        product_name: str
        secret: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                partner_name: str, 
                product_name: Optional[str] = ..., 
                secret: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataProperties(Model):
        assessment_type: Union[str, AssessmentType]
        categories: Union[list[str, Categories]]
        description: str
        display_name: str
        implementation_effort: Union[str, ImplementationEffort]
        partner_data: SecurityAssessmentMetadataPartnerData
        policy_definition_id: str
        preview: bool
        remediation_description: str
        severity: Union[str, Severity]
        threats: Union[list[str, Threats]]
        user_impact: Union[str, UserImpact]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_type: Union[str, AssessmentType], 
                categories: Optional[List[Union[str, Categories]]] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                implementation_effort: Optional[Union[str, ImplementationEffort]] = ..., 
                partner_data: Optional[SecurityAssessmentMetadataPartnerData] = ..., 
                preview: Optional[bool] = ..., 
                remediation_description: Optional[str] = ..., 
                severity: Union[str, Severity], 
                threats: Optional[List[Union[str, Threats]]] = ..., 
                user_impact: Optional[Union[str, UserImpact]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataPropertiesResponse(SecurityAssessmentMetadataProperties):
        assessment_type: Union[str, AssessmentType]
        categories: Union[list[str, Categories]]
        description: str
        display_name: str
        implementation_effort: Union[str, ImplementationEffort]
        partner_data: SecurityAssessmentMetadataPartnerData
        planned_deprecation_date: str
        policy_definition_id: str
        preview: bool
        publish_dates: SecurityAssessmentMetadataPropertiesResponsePublishDates
        remediation_description: str
        severity: Union[str, Severity]
        tactics: Union[list[str, Tactics]]
        techniques: Union[list[str, Techniques]]
        threats: Union[list[str, Threats]]
        user_impact: Union[str, UserImpact]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_type: Union[str, AssessmentType], 
                categories: Optional[List[Union[str, Categories]]] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                implementation_effort: Optional[Union[str, ImplementationEffort]] = ..., 
                partner_data: Optional[SecurityAssessmentMetadataPartnerData] = ..., 
                planned_deprecation_date: Optional[str] = ..., 
                preview: Optional[bool] = ..., 
                publish_dates: Optional[SecurityAssessmentMetadataPropertiesResponsePublishDates] = ..., 
                remediation_description: Optional[str] = ..., 
                severity: Union[str, Severity], 
                tactics: Optional[List[Union[str, Tactics]]] = ..., 
                techniques: Optional[List[Union[str, Techniques]]] = ..., 
                threats: Optional[List[Union[str, Threats]]] = ..., 
                user_impact: Optional[Union[str, UserImpact]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataPropertiesResponsePublishDates(Model):
        ga: str
        public: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ga: Optional[str] = ..., 
                public: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataResponse(Resource):
        assessment_type: Union[str, AssessmentType]
        categories: Union[list[str, Categories]]
        description: str
        display_name: str
        id: str
        implementation_effort: Union[str, ImplementationEffort]
        name: str
        partner_data: SecurityAssessmentMetadataPartnerData
        planned_deprecation_date: str
        policy_definition_id: str
        preview: bool
        publish_dates: SecurityAssessmentMetadataPropertiesResponsePublishDates
        remediation_description: str
        severity: Union[str, Severity]
        tactics: Union[list[str, Tactics]]
        techniques: Union[list[str, Techniques]]
        threats: Union[list[str, Threats]]
        type: str
        user_impact: Union[str, UserImpact]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_type: Optional[Union[str, AssessmentType]] = ..., 
                categories: Optional[List[Union[str, Categories]]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                implementation_effort: Optional[Union[str, ImplementationEffort]] = ..., 
                partner_data: Optional[SecurityAssessmentMetadataPartnerData] = ..., 
                planned_deprecation_date: Optional[str] = ..., 
                preview: Optional[bool] = ..., 
                publish_dates: Optional[SecurityAssessmentMetadataPropertiesResponsePublishDates] = ..., 
                remediation_description: Optional[str] = ..., 
                severity: Optional[Union[str, Severity]] = ..., 
                tactics: Optional[List[Union[str, Tactics]]] = ..., 
                techniques: Optional[List[Union[str, Techniques]]] = ..., 
                threats: Optional[List[Union[str, Threats]]] = ..., 
                user_impact: Optional[Union[str, UserImpact]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataResponseList(Model):
        next_link: str
        value: list[SecurityAssessmentMetadataResponse]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentPartnerData(Model):
        partner_name: str
        secret: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                partner_name: str, 
                secret: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentProperties(SecurityAssessmentPropertiesBase):
        additional_data: dict[str, str]
        display_name: str
        links: AssessmentLinks
        metadata: SecurityAssessmentMetadataProperties
        partners_data: SecurityAssessmentPartnerData
        resource_details: ResourceDetails
        risk: SecurityAssessmentPropertiesBaseRisk
        status: AssessmentStatus

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_data: Optional[Dict[str, str]] = ..., 
                metadata: Optional[SecurityAssessmentMetadataProperties] = ..., 
                partners_data: Optional[SecurityAssessmentPartnerData] = ..., 
                resource_details: ResourceDetails, 
                risk: Optional[SecurityAssessmentPropertiesBaseRisk] = ..., 
                status: AssessmentStatus, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesBase(Model):
        additional_data: dict[str, str]
        display_name: str
        links: AssessmentLinks
        metadata: SecurityAssessmentMetadataProperties
        partners_data: SecurityAssessmentPartnerData
        resource_details: ResourceDetails
        risk: SecurityAssessmentPropertiesBaseRisk

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_data: Optional[Dict[str, str]] = ..., 
                metadata: Optional[SecurityAssessmentMetadataProperties] = ..., 
                partners_data: Optional[SecurityAssessmentPartnerData] = ..., 
                resource_details: ResourceDetails, 
                risk: Optional[SecurityAssessmentPropertiesBaseRisk] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesBaseRisk(Model):
        attack_paths_references: list[str]
        is_contextual_risk: bool
        level: Union[str, RiskLevel]
        paths: list[SecurityAssessmentPropertiesBaseRiskPathsItem]
        risk_factors: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                attack_paths_references: Optional[List[str]] = ..., 
                is_contextual_risk: Optional[bool] = ..., 
                level: Optional[Union[str, RiskLevel]] = ..., 
                paths: Optional[List[SecurityAssessmentPropertiesBaseRiskPathsItem]] = ..., 
                risk_factors: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesBaseRiskPathsItem(Model):
        edges: list[Components1Uu4J47SchemasSecurityassessmentpropertiesbasePropertiesRiskPropertiesPathsItemsPropertiesEdgesItems]
        id: str
        nodes: list[SecurityAssessmentPropertiesBaseRiskPathsPropertiesItemsItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                edges: Optional[List[Components1Uu4J47SchemasSecurityassessmentpropertiesbasePropertiesRiskPropertiesPathsItemsPropertiesEdgesItems]] = ..., 
                id: Optional[str] = ..., 
                nodes: Optional[List[SecurityAssessmentPropertiesBaseRiskPathsPropertiesItemsItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesBaseRiskPathsPropertiesItemsItem(Model):
        id: str
        node_properties_label: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                node_properties_label: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesResponse(SecurityAssessmentPropertiesBase):
        additional_data: dict[str, str]
        display_name: str
        links: AssessmentLinks
        metadata: SecurityAssessmentMetadataProperties
        partners_data: SecurityAssessmentPartnerData
        resource_details: ResourceDetails
        risk: SecurityAssessmentPropertiesBaseRisk
        status: AssessmentStatusResponse

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_data: Optional[Dict[str, str]] = ..., 
                metadata: Optional[SecurityAssessmentMetadataProperties] = ..., 
                partners_data: Optional[SecurityAssessmentPartnerData] = ..., 
                resource_details: ResourceDetails, 
                risk: Optional[SecurityAssessmentPropertiesBaseRisk] = ..., 
                status: AssessmentStatusResponse, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityAssessmentResponse(Resource):
        additional_data: dict[str, str]
        display_name: str
        id: str
        links: AssessmentLinks
        metadata: SecurityAssessmentMetadataProperties
        name: str
        partners_data: SecurityAssessmentPartnerData
        resource_details: ResourceDetails
        risk: SecurityAssessmentPropertiesBaseRisk
        status: AssessmentStatusResponse
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_data: Optional[Dict[str, str]] = ..., 
                metadata: Optional[SecurityAssessmentMetadataProperties] = ..., 
                partners_data: Optional[SecurityAssessmentPartnerData] = ..., 
                resource_details: Optional[ResourceDetails] = ..., 
                risk: Optional[SecurityAssessmentPropertiesBaseRisk] = ..., 
                status: Optional[AssessmentStatusResponse] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityConnector(TrackedResource):
        environment_data: EnvironmentData
        environment_name: Union[str, CloudName]
        etag: str
        hierarchy_identifier: str
        hierarchy_identifier_trial_end_date: datetime
        id: str
        kind: str
        location: str
        name: str
        offerings: list[CloudOffering]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                environment_data: Optional[EnvironmentData] = ..., 
                environment_name: Optional[Union[str, CloudName]] = ..., 
                etag: Optional[str] = ..., 
                hierarchy_identifier: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                offerings: Optional[List[CloudOffering]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityConnectorsList(Model):
        next_link: str
        value: list[SecurityConnector]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[SecurityConnector], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityContact(Resource):
        emails: str
        id: str
        is_enabled: bool
        name: str
        notifications_by_role: SecurityContactPropertiesNotificationsByRole
        notifications_sources: list[NotificationsSource]
        phone: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                emails: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                notifications_by_role: Optional[SecurityContactPropertiesNotificationsByRole] = ..., 
                notifications_sources: Optional[List[NotificationsSource]] = ..., 
                phone: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityContactList(Model):
        next_link: str
        value: list[SecurityContact]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[SecurityContact], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityContactName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.security.models.SecurityContactPropertiesNotificationsByRole(Model):
        roles: Union[list[str, SecurityContactRole]]
        state: Union[str, State]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                roles: Optional[List[Union[str, SecurityContactRole]]] = ..., 
                state: Optional[Union[str, State]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityContactRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_ADMIN = "AccountAdmin"
        CONTRIBUTOR = "Contributor"
        OWNER = "Owner"
        SERVICE_ADMIN = "ServiceAdmin"


    class azure.mgmt.security.models.SecurityFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NGFW = "Ngfw"
        SAAS_WAF = "SaasWaf"
        VA = "Va"
        WAF = "Waf"


    class azure.mgmt.security.models.SecurityIssue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS_ACCESS = "AnonymousAccess"
        BEST_PRACTICES = "BestPractices"
        EXCESSIVE_PERMISSIONS = "ExcessivePermissions"
        NETWORK_EXPOSURE = "NetworkExposure"
        TRAFFIC_ENCRYPTION = "TrafficEncryption"
        VULNERABILITY = "Vulnerability"


    class azure.mgmt.security.models.SecurityOperator(Resource):
        id: str
        identity: Identity
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityOperatorList(Model):
        value: list[SecurityOperator]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[SecurityOperator], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecuritySolution(Resource, Location):
        id: str
        location: str
        name: str
        protection_status: str
        provisioning_state: Union[str, ProvisioningState]
        security_family: Union[str, SecurityFamily]
        template: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                protection_status: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                security_family: Optional[Union[str, SecurityFamily]] = ..., 
                template: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecuritySolutionList(Model):
        next_link: str
        value: list[SecuritySolution]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[SecuritySolution]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecuritySolutionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.SecuritySolutionsReferenceData(Resource, Location):
        alert_vendor_name: str
        id: str
        location: str
        name: str
        package_info_url: str
        product_name: str
        publisher: str
        publisher_display_name: str
        security_family: Union[str, SecurityFamily]
        template: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                alert_vendor_name: str, 
                package_info_url: str, 
                product_name: str, 
                publisher: str, 
                publisher_display_name: str, 
                security_family: Union[str, SecurityFamily], 
                template: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecuritySolutionsReferenceDataList(Model):
        value: list[SecuritySolutionsReferenceData]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[SecuritySolutionsReferenceData]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityStandard(Resource):
        assessments: list[PartialAssessmentProperties]
        cloud_providers: Union[list[str, StandardSupportedCloud]]
        description: str
        display_name: str
        id: str
        metadata: StandardMetadata
        name: str
        policy_set_definition_id: str
        standard_type: Union[str, StandardType]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessments: Optional[List[PartialAssessmentProperties]] = ..., 
                cloud_providers: Optional[List[Union[str, StandardSupportedCloud]]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                metadata: Optional[StandardMetadata] = ..., 
                policy_set_definition_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityStandardList(Model):
        next_link: str
        value: list[SecurityStandard]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecuritySubAssessment(Resource):
        additional_data: AdditionalData
        category: str
        description: str
        display_name: str
        id: str
        id_properties_id: str
        impact: str
        name: str
        remediation: str
        resource_details: ResourceDetails
        status: SubAssessmentStatus
        time_generated: datetime
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_data: Optional[AdditionalData] = ..., 
                resource_details: Optional[ResourceDetails] = ..., 
                status: Optional[SubAssessmentStatus] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecuritySubAssessmentList(Model):
        next_link: str
        value: list[SecuritySubAssessment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityTask(Resource):
        creation_time_utc: datetime
        id: str
        last_state_change_time_utc: datetime
        name: str
        security_task_parameters: SecurityTaskParameters
        state: str
        sub_state: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                security_task_parameters: Optional[SecurityTaskParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityTaskList(Model):
        next_link: str
        value: list[SecurityTask]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SecurityTaskParameters(Model):
        additional_properties: dict[str, any]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SensitiveDataDiscoveryProperties(Model):
        is_enabled: bool
        operation_status: OperationStatus

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SensitivityLabel(Model):
        description: str
        display_name: str
        enabled: bool
        order: int
        rank: Union[str, Rank]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                order: Optional[int] = ..., 
                rank: Optional[Union[str, Rank]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ServerVulnerabilityAssessment(Resource):
        id: str
        name: str
        provisioning_state: Union[str, ServerVulnerabilityAssessmentPropertiesProvisioningState]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentPropertiesProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DEPROVISIONING = "Deprovisioning"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsAzureSettingSelectedProvider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MDE_TVM = "MdeTvm"


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsList(Model):
        value: list[ServerVulnerabilityAssessment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ServerVulnerabilityAssessment]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsSetting(ResourceAutoGenerated):
        id: str
        kind: Union[str, ServerVulnerabilityAssessmentsSettingKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsSettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVERS_SETTING = "AzureServersSetting"


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsSettingKindName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVERS_SETTING = "azureServersSetting"


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsSettingsList(Model):
        next_link: str
        value: list[ServerVulnerabilityAssessmentsSetting]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ServerVulnerabilityProperties(AdditionalData):
        assessed_resource_type: Union[str, AssessedResourceType]
        cve: list[azure.mgmt.security.models.CVE]
        cvss: dict[str, azure.mgmt.security.models.CVSS]
        patchable: bool
        published_time: datetime
        threat: str
        type: str
        vendor_references: list[VendorReference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ServicePrincipalProperties(Model):
        application_id: str
        secret: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                secret: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Setting(Resource):
        id: str
        kind: Union[str, SettingKind]
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_SUPPRESSION_SETTING = "AlertSuppressionSetting"
        ALERT_SYNC_SETTINGS = "AlertSyncSettings"
        DATA_EXPORT_SETTINGS = "DataExportSettings"


    class azure.mgmt.security.models.SettingName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT = "current"


    class azure.mgmt.security.models.SettingNameAutoGenerated(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MCAS = "MCAS"
        SENTINEL = "Sentinel"
        WDATP = "WDATP"
        WDATP_EXCLUDE_LINUX_PUBLIC_PREVIEW = "WDATP_EXCLUDE_LINUX_PUBLIC_PREVIEW"
        WDATP_UNIFIED_SOLUTION = "WDATP_UNIFIED_SOLUTION"


    class azure.mgmt.security.models.SettingsList(Model):
        next_link: str
        value: list[Setting]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Setting]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.SeverityEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.Software(Resource):
        device_id: str
        end_of_support_date: str
        end_of_support_status: Union[str, EndOfSupportStatus]
        first_seen_at: str
        id: str
        name: str
        number_of_known_vulnerabilities: int
        os_platform: str
        software_name: str
        type: str
        vendor: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_id: Optional[str] = ..., 
                end_of_support_date: Optional[str] = ..., 
                end_of_support_status: Optional[Union[str, EndOfSupportStatus]] = ..., 
                first_seen_at: Optional[str] = ..., 
                number_of_known_vulnerabilities: Optional[int] = ..., 
                os_platform: Optional[str] = ..., 
                software_name: Optional[str] = ..., 
                vendor: Optional[str] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SoftwaresList(Model):
        next_link: str
        value: list[Software]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Software]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Source(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        ON_PREMISE = "OnPremise"
        ON_PREMISE_SQL = "OnPremiseSql"


    class azure.mgmt.security.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT = "Alert"
        ATTACK_PATH = "AttackPath"


    class azure.mgmt.security.models.SqlServerVulnerabilityProperties(AdditionalData):
        assessed_resource_type: Union[str, AssessedResourceType]
        query: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.StandardAssignment(Resource):
        assigned_standard: AssignedStandardItem
        attestation_data: StandardAssignmentPropertiesAttestationData
        description: str
        display_name: str
        effect: Union[str, Effect]
        excluded_scopes: list[str]
        exemption_data: StandardAssignmentPropertiesExemptionData
        expires_on: datetime
        id: str
        metadata: StandardAssignmentMetadata
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assigned_standard: Optional[AssignedStandardItem] = ..., 
                attestation_data: Optional[StandardAssignmentPropertiesAttestationData] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                effect: Optional[Union[str, Effect]] = ..., 
                excluded_scopes: Optional[List[str]] = ..., 
                exemption_data: Optional[StandardAssignmentPropertiesExemptionData] = ..., 
                expires_on: Optional[datetime] = ..., 
                metadata: Optional[StandardAssignmentMetadata] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.StandardAssignmentMetadata(Model):
        created_by: str
        created_on: datetime
        last_updated_by: str
        last_updated_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.StandardAssignmentPropertiesAttestationData(Model):
        assigned_assessment: AssignedAssessmentItem
        compliance_date: datetime
        compliance_state: Union[str, AttestationComplianceState]
        evidence: list[AttestationEvidence]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assigned_assessment: Optional[AssignedAssessmentItem] = ..., 
                compliance_state: Optional[Union[str, AttestationComplianceState]] = ..., 
                evidence: Optional[List[AttestationEvidence]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.StandardAssignmentPropertiesExemptionData(Model):
        assigned_assessment: AssignedAssessmentItem
        exemption_category: Union[str, ExemptionCategory]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assigned_assessment: Optional[AssignedAssessmentItem] = ..., 
                exemption_category: Optional[Union[str, ExemptionCategory]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.StandardAssignmentsList(Model):
        next_link: str
        value: list[StandardAssignment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.StandardMetadata(Model):
        created_by: str
        created_on: datetime
        last_updated_by: str
        last_updated_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.StandardSupportedCloud(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "AWS"
        AZURE = "Azure"
        GCP = "GCP"


    class azure.mgmt.security.models.StandardType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANCE = "Compliance"
        CUSTOM = "Custom"
        DEFAULT = "Default"


    class azure.mgmt.security.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PASSED = "Passed"
        SKIPPED = "Skipped"
        UNSUPPORTED = "Unsupported"


    class azure.mgmt.security.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INITIATED = "Initiated"
        REVOKED = "Revoked"


    class azure.mgmt.security.models.StatusAutoGenerated(Model):
        code: Union[str, StatusName]
        first_evaluation_date: datetime
        last_scanned_date: datetime
        reason: str
        status_change_date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[Union[str, StatusName]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.StatusName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_APPLICABLE = "NotApplicable"
        NOT_HEALTHY = "NotHealthy"


    class azure.mgmt.security.models.StatusReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPIRED = "Expired"
        NEWER_REQUEST_INITIATED = "NewerRequestInitiated"
        USER_REQUESTED = "UserRequested"


    class azure.mgmt.security.models.SubAssessmentStatus(Model):
        cause: str
        code: Union[str, SubAssessmentStatusCode]
        description: str
        severity: Union[str, Severity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SubAssessmentStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_APPLICABLE = "NotApplicable"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.security.models.SubPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1 = "P1"
        P2 = "P2"


    class azure.mgmt.security.models.SupportedCloudEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "AWS"
        GCP = "GCP"


    class azure.mgmt.security.models.SuppressionAlertsScope(Model):
        all_of: list[ScopeElement]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                all_of: List[ScopeElement], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Tactics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLECTION = "Collection"
        COMMAND_AND_CONTROL = "Command and Control"
        CREDENTIAL_ACCESS = "Credential Access"
        DEFENSE_EVASION = "Defense Evasion"
        DISCOVERY = "Discovery"
        EXECUTION = "Execution"
        EXFILTRATION = "Exfiltration"
        IMPACT = "Impact"
        INITIAL_ACCESS = "Initial Access"
        LATERAL_MOVEMENT = "Lateral Movement"
        PERSISTENCE = "Persistence"
        PRIVILEGE_ESCALATION = "Privilege Escalation"
        RECONNAISSANCE = "Reconnaissance"
        RESOURCE_DEVELOPMENT = "Resource Development"


    class azure.mgmt.security.models.Tags(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TagsResource(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TargetBranchConfiguration(Model):
        annotate_default_branch: Union[str, AnnotateDefaultBranchState]
        branch_names: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotate_default_branch: Optional[Union[str, AnnotateDefaultBranchState]] = ..., 
                branch_names: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TaskUpdateActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATE = "Activate"
        CLOSE = "Close"
        DISMISS = "Dismiss"
        RESOLVE = "Resolve"
        START = "Start"


    class azure.mgmt.security.models.Techniques(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABUSE_ELEVATION_CONTROL_MECHANISM = "Abuse Elevation Control Mechanism"
        ACCESS_TOKEN_MANIPULATION = "Access Token Manipulation"
        ACCOUNT_DISCOVERY = "Account Discovery"
        ACCOUNT_MANIPULATION = "Account Manipulation"
        ACTIVE_SCANNING = "Active Scanning"
        APPLICATION_LAYER_PROTOCOL = "Application Layer Protocol"
        AUDIO_CAPTURE = "Audio Capture"
        BOOT_OR_LOGON_AUTOSTART_EXECUTION = "Boot or Logon Autostart Execution"
        BOOT_OR_LOGON_INITIALIZATION_SCRIPTS = "Boot or Logon Initialization Scripts"
        BRUTE_FORCE = "Brute Force"
        CLOUD_INFRASTRUCTURE_DISCOVERY = "Cloud Infrastructure Discovery"
        CLOUD_SERVICE_DASHBOARD = "Cloud Service Dashboard"
        CLOUD_SERVICE_DISCOVERY = "Cloud Service Discovery"
        COMMAND_AND_SCRIPTING_INTERPRETER = "Command and Scripting Interpreter"
        COMPROMISE_CLIENT_SOFTWARE_BINARY = "Compromise Client Software Binary"
        COMPROMISE_INFRASTRUCTURE = "Compromise Infrastructure"
        CONTAINER_AND_RESOURCE_DISCOVERY = "Container and Resource Discovery"
        CREATE_ACCOUNT = "Create Account"
        CREATE_OR_MODIFY_SYSTEM_PROCESS = "Create or Modify System Process"
        CREDENTIALS_FROM_PASSWORD_STORES = "Credentials from Password Stores"
        DATA_DESTRUCTION = "Data Destruction"
        DATA_ENCRYPTED_FOR_IMPACT = "Data Encrypted for Impact"
        DATA_FROM_CLOUD_STORAGE_OBJECT = "Data from Cloud Storage Object"
        DATA_FROM_CONFIGURATION_REPOSITORY = "Data from Configuration Repository"
        DATA_FROM_INFORMATION_REPOSITORIES = "Data from Information Repositories"
        DATA_FROM_LOCAL_SYSTEM = "Data from Local System"
        DATA_MANIPULATION = "Data Manipulation"
        DATA_STAGED = "Data Staged"
        DEFACEMENT = "Defacement"
        DEOBFUSCATE_DECODE_FILES_OR_INFORMATION = "Deobfuscate/Decode Files or Information"
        DISK_WIPE = "Disk Wipe"
        DOMAIN_TRUST_DISCOVERY = "Domain Trust Discovery"
        DRIVE_BY_COMPROMISE = "Drive-by Compromise"
        DYNAMIC_RESOLUTION = "Dynamic Resolution"
        ENDPOINT_DENIAL_OF_SERVICE = "Endpoint Denial of Service"
        EVENT_TRIGGERED_EXECUTION = "Event Triggered Execution"
        EXFILTRATION_OVER_ALTERNATIVE_PROTOCOL = "Exfiltration Over Alternative Protocol"
        EXPLOITATION_FOR_CLIENT_EXECUTION = "Exploitation for Client Execution"
        EXPLOITATION_FOR_CREDENTIAL_ACCESS = "Exploitation for Credential Access"
        EXPLOITATION_FOR_DEFENSE_EVASION = "Exploitation for Defense Evasion"
        EXPLOITATION_FOR_PRIVILEGE_ESCALATION = "Exploitation for Privilege Escalation"
        EXPLOITATION_OF_REMOTE_SERVICES = "Exploitation of Remote Services"
        EXPLOIT_PUBLIC_FACING_APPLICATION = "Exploit Public-Facing Application"
        EXTERNAL_REMOTE_SERVICES = "External Remote Services"
        FALLBACK_CHANNELS = "Fallback Channels"
        FILE_AND_DIRECTORY_DISCOVERY = "File and Directory Discovery"
        FILE_AND_DIRECTORY_PERMISSIONS_MODIFICATION = "File and Directory Permissions Modification"
        GATHER_VICTIM_NETWORK_INFORMATION = "Gather Victim Network Information"
        HIDE_ARTIFACTS = "Hide Artifacts"
        HIJACK_EXECUTION_FLOW = "Hijack Execution Flow"
        IMPAIR_DEFENSES = "Impair Defenses"
        IMPLANT_CONTAINER_IMAGE = "Implant Container Image"
        INDICATOR_REMOVAL_ON_HOST = "Indicator Removal on Host"
        INDIRECT_COMMAND_EXECUTION = "Indirect Command Execution"
        INGRESS_TOOL_TRANSFER = "Ingress Tool Transfer"
        INPUT_CAPTURE = "Input Capture"
        INTER_PROCESS_COMMUNICATION = "Inter-Process Communication"
        LATERAL_TOOL_TRANSFER = "Lateral Tool Transfer"
        MAN_IN_THE_MIDDLE = "Man-in-the-Middle"
        MASQUERADING = "Masquerading"
        MODIFY_AUTHENTICATION_PROCESS = "Modify Authentication Process"
        MODIFY_REGISTRY = "Modify Registry"
        NETWORK_DENIAL_OF_SERVICE = "Network Denial of Service"
        NETWORK_SERVICE_SCANNING = "Network Service Scanning"
        NETWORK_SNIFFING = "Network Sniffing"
        NON_APPLICATION_LAYER_PROTOCOL = "Non-Application Layer Protocol"
        NON_STANDARD_PORT = "Non-Standard Port"
        OBFUSCATED_FILES_OR_INFORMATION = "Obfuscated Files or Information"
        OBTAIN_CAPABILITIES = "Obtain Capabilities"
        OFFICE_APPLICATION_STARTUP = "Office Application Startup"
        OS_CREDENTIAL_DUMPING = "OS Credential Dumping"
        PERMISSION_GROUPS_DISCOVERY = "Permission Groups Discovery"
        PHISHING = "Phishing"
        PRE_OS_BOOT = "Pre-OS Boot"
        PROCESS_DISCOVERY = "Process Discovery"
        PROCESS_INJECTION = "Process Injection"
        PROTOCOL_TUNNELING = "Protocol Tunneling"
        PROXY = "Proxy"
        QUERY_REGISTRY = "Query Registry"
        REMOTE_ACCESS_SOFTWARE = "Remote Access Software"
        REMOTE_SERVICES = "Remote Services"
        REMOTE_SERVICE_SESSION_HIJACKING = "Remote Service Session Hijacking"
        REMOTE_SYSTEM_DISCOVERY = "Remote System Discovery"
        RESOURCE_HIJACKING = "Resource Hijacking"
        SCHEDULED_TASK_JOB = "Scheduled Task/Job"
        SCREEN_CAPTURE = "Screen Capture"
        SEARCH_VICTIM_OWNED_WEBSITES = "Search Victim-Owned Websites"
        SERVER_SOFTWARE_COMPONENT = "Server Software Component"
        SERVICE_STOP = "Service Stop"
        SIGNED_BINARY_PROXY_EXECUTION = "Signed Binary Proxy Execution"
        SOFTWARE_DEPLOYMENT_TOOLS = "Software Deployment Tools"
        SQL_STORED_PROCEDURES = "SQL Stored Procedures"
        STEAL_OR_FORGE_KERBEROS_TICKETS = "Steal or Forge Kerberos Tickets"
        SUBVERT_TRUST_CONTROLS = "Subvert Trust Controls"
        SUPPLY_CHAIN_COMPROMISE = "Supply Chain Compromise"
        SYSTEM_INFORMATION_DISCOVERY = "System Information Discovery"
        TAINT_SHARED_CONTENT = "Taint Shared Content"
        TRAFFIC_SIGNALING = "Traffic Signaling"
        TRANSFER_DATA_TO_CLOUD_ACCOUNT = "Transfer Data to Cloud Account"
        TRUSTED_RELATIONSHIP = "Trusted Relationship"
        UNSECURED_CREDENTIALS = "Unsecured Credentials"
        USER_EXECUTION = "User Execution"
        VALID_ACCOUNTS = "Valid Accounts"
        WINDOWS_MANAGEMENT_INSTRUMENTATION = "Windows Management Instrumentation"


    class azure.mgmt.security.models.Threats(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_BREACH = "accountBreach"
        DATA_EXFILTRATION = "dataExfiltration"
        DATA_SPILLAGE = "dataSpillage"
        DENIAL_OF_SERVICE = "denialOfService"
        ELEVATION_OF_PRIVILEGE = "elevationOfPrivilege"
        MALICIOUS_INSIDER = "maliciousInsider"
        MISSING_COVERAGE = "missingCoverage"
        THREAT_RESISTANCE = "threatResistance"


    class azure.mgmt.security.models.ThresholdCustomAlertRule(CustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TimeWindowCustomAlertRule(ThresholdCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TopologyList(Model):
        next_link: str
        value: list[TopologyResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TopologyResource(Resource, Location):
        calculated_date_time: datetime
        id: str
        location: str
        name: str
        topology_resources: list[TopologySingleResource]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TopologySingleResource(Model):
        children: list[TopologySingleResourceChild]
        location: str
        network_zones: str
        parents: list[TopologySingleResourceParent]
        recommendations_exist: bool
        resource_id: str
        severity: str
        topology_score: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TopologySingleResourceChild(Model):
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TopologySingleResourceParent(Model):
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TrackedResource(Resource, AzureTrackedResourceLocation, Kind, ETag, Tags):
        etag: str
        id: str
        kind: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TrackedResourceAutoGenerated(ResourceAutoGenerated2):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.TwinUpdatesNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUALYS = "Qualys"
        TVM = "TVM"


    class azure.mgmt.security.models.UnauthorizedOperationsNotInAllowedRange(TimeWindowCustomAlertRule):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: str
        time_window_size: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int, 
                time_window_size: timedelta, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.UnmaskedIpLoggingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.UpdateIotSecuritySolutionData(TagsResource):
        recommendations_configuration: list[RecommendationConfigurationProperties]
        tags: dict[str, str]
        user_defined_resources: UserDefinedResourcesProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recommendations_configuration: Optional[List[RecommendationConfigurationProperties]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                user_defined_resources: Optional[UserDefinedResourcesProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.UpdateSensitivitySettingsRequest(Model):
        sensitive_info_types_ids: list[str]
        sensitivity_threshold_label_id: str
        sensitivity_threshold_label_order: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sensitive_info_types_ids: List[str], 
                sensitivity_threshold_label_id: Optional[str] = ..., 
                sensitivity_threshold_label_order: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.UserDefinedResourcesProperties(Model):
        query: str
        query_subscriptions: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                query: str, 
                query_subscriptions: List[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.UserImpact(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MODERATE = "Moderate"


    class azure.mgmt.security.models.VaRule(Model):
        benchmark_references: list[BenchmarkReference]
        category: str
        description: str
        query_check: QueryCheck
        rationale: str
        rule_id: str
        rule_type: Union[str, RuleType]
        severity: Union[str, RuleSeverity]
        title: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                benchmark_references: Optional[List[BenchmarkReference]] = ..., 
                category: Optional[str] = ..., 
                description: Optional[str] = ..., 
                query_check: Optional[QueryCheck] = ..., 
                rationale: Optional[str] = ..., 
                rule_id: Optional[str] = ..., 
                rule_type: Optional[Union[str, RuleType]] = ..., 
                severity: Optional[Union[str, RuleSeverity]] = ..., 
                title: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.ValueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IP_CIDR = "IpCidr"
        STRING = "String"


    class azure.mgmt.security.models.VendorReference(Model):
        link: str
        title: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.VmScannersAws(VmScannersBase):
        cloud_role_arn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.VmScannersBase(Model):
        configuration: VmScannersBaseConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.VmScannersBaseConfiguration(Model):
        exclusion_tags: dict[str, str]
        scanning_mode: Union[str, ScanningMode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                exclusion_tags: Optional[Dict[str, str]] = ..., 
                scanning_mode: Optional[Union[str, ScanningMode]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.VmScannersGcp(VmScannersBase):
        configuration: VmScannersBaseConfiguration
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.WorkspaceSetting(Resource):
        id: str
        name: str
        scope: str
        type: str
        workspace_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scope: Optional[str] = ..., 
                workspace_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.security.models.WorkspaceSettingList(Model):
        next_link: str
        value: list[WorkspaceSetting]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[WorkspaceSetting], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.mgmt.security.operations

    class azure.mgmt.security.operations.APICollectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_onboard_azure_api_management_api(
                self, 
                resource_group_name: str, 
                service_name: str, 
                api_id: str, 
                **kwargs: Any
            ) -> LROPoller[ApiCollection]: ...

        @distributed_trace
        def get_by_azure_api_management_service(
                self, 
                resource_group_name: str, 
                service_name: str, 
                api_id: str, 
                **kwargs: Any
            ) -> ApiCollection: ...

        @distributed_trace
        def list_by_azure_api_management_service(
                self, 
                resource_group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApiCollection]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApiCollection]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ApiCollection]: ...

        @distributed_trace
        def offboard_azure_api_management_api(
                self, 
                resource_group_name: str, 
                service_name: str, 
                api_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.security.operations.AdvancedThreatProtectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_id: str, 
                advanced_threat_protection_setting: AdvancedThreatProtectionSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdvancedThreatProtectionSetting: ...

        @overload
        def create(
                self, 
                resource_id: str, 
                advanced_threat_protection_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdvancedThreatProtectionSetting: ...

        @distributed_trace
        def get(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> AdvancedThreatProtectionSetting: ...


    class azure.mgmt.security.operations.AlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_simulate(
                self, 
                asc_location: str, 
                alert_simulator_request_body: AlertSimulatorRequestBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_simulate(
                self, 
                asc_location: str, 
                alert_simulator_request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_resource_group_level(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def get_subscription_level(
                self, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Alert]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Alert]: ...

        @distributed_trace
        def list_resource_group_level_by_region(
                self, 
                asc_location: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Alert]: ...

        @distributed_trace
        def list_subscription_level_by_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> ItemPaged[Alert]: ...

        @distributed_trace
        def update_resource_group_level_state_to_activate(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_resource_group_level_state_to_dismiss(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_resource_group_level_state_to_in_progress(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_resource_group_level_state_to_resolve(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_subscription_level_state_to_activate(
                self, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_subscription_level_state_to_dismiss(
                self, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_subscription_level_state_to_in_progress(
                self, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_subscription_level_state_to_resolve(
                self, 
                asc_location: str, 
                alert_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.security.operations.AlertsSuppressionRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                alerts_suppression_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                alerts_suppression_rule_name: str, 
                **kwargs: Any
            ) -> AlertsSuppressionRule: ...

        @distributed_trace
        def list(
                self, 
                alert_type: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[AlertsSuppressionRule]: ...

        @overload
        def update(
                self, 
                alerts_suppression_rule_name: str, 
                alerts_suppression_rule: AlertsSuppressionRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertsSuppressionRule: ...

        @overload
        def update(
                self, 
                alerts_suppression_rule_name: str, 
                alerts_suppression_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertsSuppressionRule: ...


    class azure.mgmt.security.operations.AllowedConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                connection_type: Union[str, ConnectionType], 
                **kwargs: Any
            ) -> AllowedConnectionsResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[AllowedConnectionsResource]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> ItemPaged[AllowedConnectionsResource]: ...


    class azure.mgmt.security.operations.ApplicationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                application_id: str, 
                application: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        def create_or_update(
                self, 
                application_id: str, 
                application: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace
        def delete(
                self, 
                application_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                application_id: str, 
                **kwargs: Any
            ) -> Application: ...


    class azure.mgmt.security.operations.ApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Application]: ...


    class azure.mgmt.security.operations.AssessmentsMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_in_subscription(
                self, 
                assessment_metadata_name: str, 
                assessment_metadata: SecurityAssessmentMetadataResponse, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityAssessmentMetadataResponse: ...

        @overload
        def create_in_subscription(
                self, 
                assessment_metadata_name: str, 
                assessment_metadata: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityAssessmentMetadataResponse: ...

        @distributed_trace
        def delete_in_subscription(
                self, 
                assessment_metadata_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                assessment_metadata_name: str, 
                **kwargs: Any
            ) -> SecurityAssessmentMetadataResponse: ...

        @distributed_trace
        def get_in_subscription(
                self, 
                assessment_metadata_name: str, 
                **kwargs: Any
            ) -> SecurityAssessmentMetadataResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SecurityAssessmentMetadataResponse]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SecurityAssessmentMetadataResponse]: ...


    class azure.mgmt.security.operations.AssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_id: str, 
                assessment_name: str, 
                assessment: SecurityAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityAssessmentResponse: ...

        @overload
        def create_or_update(
                self, 
                resource_id: str, 
                assessment_name: str, 
                assessment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityAssessmentResponse: ...

        @distributed_trace
        def delete(
                self, 
                resource_id: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_id: str, 
                assessment_name: str, 
                expand: Optional[Union[str, ExpandEnum]] = None, 
                **kwargs: Any
            ) -> SecurityAssessmentResponse: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[SecurityAssessmentResponse]: ...


    class azure.mgmt.security.operations.AutoProvisioningSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                setting_name: str, 
                setting: AutoProvisioningSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoProvisioningSetting: ...

        @overload
        def create(
                self, 
                setting_name: str, 
                setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoProvisioningSetting: ...

        @distributed_trace
        def get(
                self, 
                setting_name: str, 
                **kwargs: Any
            ) -> AutoProvisioningSetting: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[AutoProvisioningSetting]: ...


    class azure.mgmt.security.operations.AutomationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: Automation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Automation: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Automation: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                **kwargs: Any
            ) -> Automation: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Automation]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Automation]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: AutomationUpdateModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Automation: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Automation: ...

        @overload
        def validate(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: Automation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationValidationStatus: ...

        @overload
        def validate(
                self, 
                resource_group_name: str, 
                automation_name: str, 
                automation: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationValidationStatus: ...


    class azure.mgmt.security.operations.AzureDevOpsOrgsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                azure_dev_ops_org: AzureDevOpsOrg, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsOrg]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                azure_dev_ops_org: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsOrg]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                azure_dev_ops_org: AzureDevOpsOrg, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsOrg]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                azure_dev_ops_org: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsOrg]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                **kwargs: Any
            ) -> AzureDevOpsOrg: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureDevOpsOrg]: ...

        @distributed_trace
        def list_available(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> AzureDevOpsOrgListResponse: ...


    class azure.mgmt.security.operations.AzureDevOpsProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                azure_dev_ops_project: AzureDevOpsProject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsProject]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                azure_dev_ops_project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsProject]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                azure_dev_ops_project: AzureDevOpsProject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsProject]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                azure_dev_ops_project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsProject]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AzureDevOpsProject: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureDevOpsProject]: ...


    class azure.mgmt.security.operations.AzureDevOpsReposOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                repo_name: str, 
                azure_dev_ops_repository: AzureDevOpsRepository, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsRepository]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                repo_name: str, 
                azure_dev_ops_repository: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsRepository]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                repo_name: str, 
                azure_dev_ops_repository: AzureDevOpsRepository, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsRepository]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                repo_name: str, 
                azure_dev_ops_repository: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsRepository]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                repo_name: str, 
                **kwargs: Any
            ) -> AzureDevOpsRepository: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                org_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureDevOpsRepository]: ...


    class azure.mgmt.security.operations.ComplianceResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_id: str, 
                compliance_result_name: str, 
                **kwargs: Any
            ) -> ComplianceResult: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[ComplianceResult]: ...


    class azure.mgmt.security.operations.CompliancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                compliance_name: str, 
                **kwargs: Any
            ) -> Compliance: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[Compliance]: ...


    class azure.mgmt.security.operations.ConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                connector_name: str, 
                connector_setting: ConnectorSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectorSetting: ...

        @overload
        def create_or_update(
                self, 
                connector_name: str, 
                connector_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectorSetting: ...

        @distributed_trace
        def delete(
                self, 
                connector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                connector_name: str, 
                **kwargs: Any
            ) -> ConnectorSetting: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ConnectorSetting]: ...


    class azure.mgmt.security.operations.CustomAssessmentAutomationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                custom_assessment_automation_name: str, 
                custom_assessment_automation_body: CustomAssessmentAutomationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomAssessmentAutomation: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                custom_assessment_automation_name: str, 
                custom_assessment_automation_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomAssessmentAutomation: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                custom_assessment_automation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                custom_assessment_automation_name: str, 
                **kwargs: Any
            ) -> CustomAssessmentAutomation: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CustomAssessmentAutomation]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[CustomAssessmentAutomation]: ...


    class azure.mgmt.security.operations.CustomEntityStoreAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                custom_entity_store_assignment_name: str, 
                custom_entity_store_assignment_request_body: CustomEntityStoreAssignmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomEntityStoreAssignment: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                custom_entity_store_assignment_name: str, 
                custom_entity_store_assignment_request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomEntityStoreAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                custom_entity_store_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                custom_entity_store_assignment_name: str, 
                **kwargs: Any
            ) -> CustomEntityStoreAssignment: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CustomEntityStoreAssignment]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[CustomEntityStoreAssignment]: ...


    class azure.mgmt.security.operations.CustomRecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                custom_recommendation_name: str, 
                custom_recommendation_body: CustomRecommendation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomRecommendation: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                custom_recommendation_name: str, 
                custom_recommendation_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomRecommendation: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                custom_recommendation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                custom_recommendation_name: str, 
                **kwargs: Any
            ) -> CustomRecommendation: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[CustomRecommendation]: ...


    class azure.mgmt.security.operations.DefenderForStorageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel_malware_scan(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                scan_id: str, 
                **kwargs: Any
            ) -> MalwareScan: ...

        @overload
        def create(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                defender_for_storage_setting: DefenderForStorageSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @overload
        def create(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                defender_for_storage_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @distributed_trace
        def get(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @distributed_trace
        def get_malware_scan(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                scan_id: str, 
                **kwargs: Any
            ) -> MalwareScan: ...

        @distributed_trace
        def start_malware_scan(
                self, 
                resource_id: str, 
                setting_name: Union[str, SettingName], 
                **kwargs: Any
            ) -> MalwareScan: ...


    class azure.mgmt.security.operations.DevOpsConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                dev_ops_configuration: DevOpsConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevOpsConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                dev_ops_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevOpsConfiguration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                dev_ops_configuration: DevOpsConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevOpsConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                dev_ops_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevOpsConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> DevOpsConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DevOpsConfiguration]: ...


    class azure.mgmt.security.operations.DevOpsOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                operation_result_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.security.operations.DeviceSecurityGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_id: str, 
                device_security_group_name: str, 
                device_security_group: DeviceSecurityGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeviceSecurityGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_id: str, 
                device_security_group_name: str, 
                device_security_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeviceSecurityGroup: ...

        @distributed_trace
        def delete(
                self, 
                resource_id: str, 
                device_security_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_id: str, 
                device_security_group_name: str, 
                **kwargs: Any
            ) -> DeviceSecurityGroup: ...

        @distributed_trace
        def list(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> ItemPaged[DeviceSecurityGroup]: ...


    class azure.mgmt.security.operations.DiscoveredSecuritySolutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                discovered_security_solution_name: str, 
                **kwargs: Any
            ) -> DiscoveredSecuritySolution: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DiscoveredSecuritySolution]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> ItemPaged[DiscoveredSecuritySolution]: ...


    class azure.mgmt.security.operations.ExternalSecuritySolutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                external_security_solutions_name: str, 
                **kwargs: Any
            ) -> ExternalSecuritySolution: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ExternalSecuritySolution]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> ItemPaged[ExternalSecuritySolution]: ...


    class azure.mgmt.security.operations.GitHubOwnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                **kwargs: Any
            ) -> GitHubOwner: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GitHubOwner]: ...

        @distributed_trace
        def list_available(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> GitHubOwnerListResponse: ...


    class azure.mgmt.security.operations.GitHubReposOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                repo_name: str, 
                **kwargs: Any
            ) -> GitHubRepository: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GitHubRepository]: ...


    class azure.mgmt.security.operations.GitLabGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                group_fq_name: str, 
                **kwargs: Any
            ) -> GitLabGroup: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GitLabGroup]: ...

        @distributed_trace
        def list_available(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> GitLabGroupListResponse: ...


    class azure.mgmt.security.operations.GitLabProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                group_fq_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> GitLabProject: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                group_fq_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GitLabProject]: ...


    class azure.mgmt.security.operations.GitLabSubgroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                group_fq_name: str, 
                **kwargs: Any
            ) -> GitLabGroupListResponse: ...


    class azure.mgmt.security.operations.GovernanceAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                assessment_name: str, 
                assignment_key: str, 
                governance_assignment: GovernanceAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GovernanceAssignment: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                assessment_name: str, 
                assignment_key: str, 
                governance_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GovernanceAssignment: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                assessment_name: str, 
                assignment_key: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                assessment_name: str, 
                assignment_key: str, 
                **kwargs: Any
            ) -> GovernanceAssignment: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GovernanceAssignment]: ...


    class azure.mgmt.security.operations.GovernanceRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                scope: str, 
                rule_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_execute(
                self, 
                scope: str, 
                rule_id: str, 
                execute_governance_rule_params: Optional[ExecuteGovernanceRuleParams] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_execute(
                self, 
                scope: str, 
                rule_id: str, 
                execute_governance_rule_params: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                rule_id: str, 
                governance_rule: GovernanceRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GovernanceRule: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                rule_id: str, 
                governance_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GovernanceRule: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                rule_id: str, 
                **kwargs: Any
            ) -> GovernanceRule: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[GovernanceRule]: ...

        @distributed_trace
        def operation_results(
                self, 
                scope: str, 
                rule_id: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[OperationResultAutoGenerated]: ...


    class azure.mgmt.security.operations.HealthReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_id: str, 
                health_report_name: str, 
                **kwargs: Any
            ) -> HealthReport: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[HealthReport]: ...


    class azure.mgmt.security.operations.InformationProtectionPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                information_protection_policy_name: Union[str, InformationProtectionPolicyName], 
                information_protection_policy: InformationProtectionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformationProtectionPolicy: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                information_protection_policy_name: Union[str, InformationProtectionPolicyName], 
                information_protection_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformationProtectionPolicy: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                information_protection_policy_name: Union[str, InformationProtectionPolicyName], 
                **kwargs: Any
            ) -> InformationProtectionPolicy: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[InformationProtectionPolicy]: ...


    class azure.mgmt.security.operations.IotSecuritySolutionAnalyticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> IoTSecuritySolutionAnalyticsModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> IoTSecuritySolutionAnalyticsModelList: ...


    class azure.mgmt.security.operations.IotSecuritySolutionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                iot_security_solution_data: IoTSecuritySolutionModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IoTSecuritySolutionModel: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                iot_security_solution_data: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IoTSecuritySolutionModel: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> IoTSecuritySolutionModel: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[IoTSecuritySolutionModel]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[IoTSecuritySolutionModel]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                update_iot_security_solution_data: UpdateIotSecuritySolutionData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IoTSecuritySolutionModel: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                update_iot_security_solution_data: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IoTSecuritySolutionModel: ...


    class azure.mgmt.security.operations.IotSecuritySolutionsAnalyticsAggregatedAlertOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def dismiss(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                aggregated_alert_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                aggregated_alert_name: str, 
                **kwargs: Any
            ) -> IoTSecurityAggregatedAlert: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[IoTSecurityAggregatedAlert]: ...


    class azure.mgmt.security.operations.IotSecuritySolutionsAnalyticsRecommendationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                aggregated_recommendation_name: str, 
                **kwargs: Any
            ) -> IoTSecurityAggregatedRecommendation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                solution_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[IoTSecurityAggregatedRecommendation]: ...


    class azure.mgmt.security.operations.JitNetworkAccessPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                body: JitNetworkAccessPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitNetworkAccessPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitNetworkAccessPolicy: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                **kwargs: Any
            ) -> JitNetworkAccessPolicy: ...

        @overload
        def initiate(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                body: JitNetworkAccessPolicyInitiateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitNetworkAccessRequest: ...

        @overload
        def initiate(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                jit_network_access_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JitNetworkAccessRequest: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[JitNetworkAccessPolicy]: ...

        @distributed_trace
        def list_by_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> ItemPaged[JitNetworkAccessPolicy]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[JitNetworkAccessPolicy]: ...

        @distributed_trace
        def list_by_resource_group_and_region(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                **kwargs: Any
            ) -> ItemPaged[JitNetworkAccessPolicy]: ...


    class azure.mgmt.security.operations.LocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> AscLocation: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[AscLocation]: ...


    class azure.mgmt.security.operations.MdeOnboardingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(self, **kwargs: Any) -> MdeOnboardingData: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> MdeOnboardingDataList: ...


    class azure.mgmt.security.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.security.operations.PricingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                scope_id: str, 
                pricing_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope_id: str, 
                pricing_name: str, 
                **kwargs: Any
            ) -> Pricing: ...

        @distributed_trace
        def list(
                self, 
                scope_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> PricingList: ...

        @overload
        def update(
                self, 
                scope_id: str, 
                pricing_name: str, 
                pricing: Pricing, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Pricing: ...

        @overload
        def update(
                self, 
                scope_id: str, 
                pricing_name: str, 
                pricing: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Pricing: ...


    class azure.mgmt.security.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_endpoint_connection_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.security.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                group_id: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> PrivateLinkResourceAutoGenerated: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResourceAutoGenerated]: ...


    class azure.mgmt.security.operations.PrivateLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_link: PrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateLinkResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_link: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateLinkResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def head(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[PrivateLinkResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_link: PrivateLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                private_link_parameters: PrivateLinkParameters, 
                private_link: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...


    class azure.mgmt.security.operations.RegulatoryComplianceAssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                regulatory_compliance_standard_name: str, 
                regulatory_compliance_control_name: str, 
                regulatory_compliance_assessment_name: str, 
                **kwargs: Any
            ) -> RegulatoryComplianceAssessment: ...

        @distributed_trace
        def list(
                self, 
                regulatory_compliance_standard_name: str, 
                regulatory_compliance_control_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[RegulatoryComplianceAssessment]: ...


    class azure.mgmt.security.operations.RegulatoryComplianceControlsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                regulatory_compliance_standard_name: str, 
                regulatory_compliance_control_name: str, 
                **kwargs: Any
            ) -> RegulatoryComplianceControl: ...

        @distributed_trace
        def list(
                self, 
                regulatory_compliance_standard_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[RegulatoryComplianceControl]: ...


    class azure.mgmt.security.operations.RegulatoryComplianceStandardsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                regulatory_compliance_standard_name: str, 
                **kwargs: Any
            ) -> RegulatoryComplianceStandard: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[RegulatoryComplianceStandard]: ...


    class azure.mgmt.security.operations.SecureScoreControlDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SecureScoreControlDefinitionItem]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SecureScoreControlDefinitionItem]: ...


    class azure.mgmt.security.operations.SecureScoreControlsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                expand: Optional[Union[str, ExpandControlsEnum]] = None, 
                **kwargs: Any
            ) -> ItemPaged[SecureScoreControlDetails]: ...

        @distributed_trace
        def list_by_secure_score(
                self, 
                secure_score_name: str, 
                expand: Optional[Union[str, ExpandControlsEnum]] = None, 
                **kwargs: Any
            ) -> ItemPaged[SecureScoreControlDetails]: ...


    class azure.mgmt.security.operations.SecureScoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                secure_score_name: str, 
                **kwargs: Any
            ) -> SecureScoreItem: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SecureScoreItem]: ...


    class azure.mgmt.security.operations.SecurityConnectorApplicationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                application_id: str, 
                application: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                application_id: str, 
                application: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                application_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                application_id: str, 
                **kwargs: Any
            ) -> Application: ...


    class azure.mgmt.security.operations.SecurityConnectorApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Application]: ...


    class azure.mgmt.security.operations.SecurityConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                security_connector: SecurityConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityConnector: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                security_connector: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityConnector: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                **kwargs: Any
            ) -> SecurityConnector: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SecurityConnector]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SecurityConnector]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                security_connector: SecurityConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityConnector: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                security_connector: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityConnector: ...


    class azure.mgmt.security.operations.SecurityContactsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                security_contact_name: Union[str, SecurityContactName], 
                security_contact: SecurityContact, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityContact: ...

        @overload
        def create(
                self, 
                security_contact_name: Union[str, SecurityContactName], 
                security_contact: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityContact: ...

        @distributed_trace
        def delete(
                self, 
                security_contact_name: Union[str, SecurityContactName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                security_contact_name: Union[str, SecurityContactName], 
                **kwargs: Any
            ) -> SecurityContact: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SecurityContact]: ...


    class azure.mgmt.security.operations.SecurityOperatorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def create_or_update(
                self, 
                pricing_name: str, 
                security_operator_name: str, 
                **kwargs: Any
            ) -> SecurityOperator: ...

        @distributed_trace
        def delete(
                self, 
                pricing_name: str, 
                security_operator_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                pricing_name: str, 
                security_operator_name: str, 
                **kwargs: Any
            ) -> SecurityOperator: ...

        @distributed_trace
        def list(
                self, 
                pricing_name: str, 
                **kwargs: Any
            ) -> SecurityOperatorList: ...


    class azure.mgmt.security.operations.SecuritySolutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                security_solution_name: str, 
                **kwargs: Any
            ) -> SecuritySolution: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SecuritySolution]: ...


    class azure.mgmt.security.operations.SecuritySolutionsReferenceDataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> SecuritySolutionsReferenceDataList: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> SecuritySolutionsReferenceDataList: ...


    class azure.mgmt.security.operations.SecurityStandardsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                standard_id: str, 
                standard: SecurityStandard, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityStandard: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                standard_id: str, 
                standard: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SecurityStandard: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                standard_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                standard_id: str, 
                **kwargs: Any
            ) -> SecurityStandard: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[SecurityStandard]: ...


    class azure.mgmt.security.operations.SensitivitySettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                sensitivity_settings: UpdateSensitivitySettingsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetSensitivitySettingsResponse: ...

        @overload
        def create_or_update(
                self, 
                sensitivity_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetSensitivitySettingsResponse: ...

        @distributed_trace
        def get(self, **kwargs: Any) -> GetSensitivitySettingsResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> GetSensitivitySettingsListResponse: ...


    class azure.mgmt.security.operations.ServerVulnerabilityAssessmentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessment: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessment: ...

        @distributed_trace
        def list_by_extended_resource(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessmentsList: ...


    class azure.mgmt.security.operations.ServerVulnerabilityAssessmentsSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                setting_kind: Union[str, ServerVulnerabilityAssessmentsSettingKindName], 
                server_vulnerability_assessments_setting: ServerVulnerabilityAssessmentsSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessmentsSetting: ...

        @overload
        def create_or_update(
                self, 
                setting_kind: Union[str, ServerVulnerabilityAssessmentsSettingKindName], 
                server_vulnerability_assessments_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessmentsSetting: ...

        @distributed_trace
        def delete(
                self, 
                setting_kind: Union[str, ServerVulnerabilityAssessmentsSettingKindName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                setting_kind: Union[str, ServerVulnerabilityAssessmentsSettingKindName], 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessmentsSetting: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ServerVulnerabilityAssessmentsSetting]: ...


    class azure.mgmt.security.operations.SettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                setting_name: Union[str, SettingNameAutoGenerated], 
                **kwargs: Any
            ) -> Setting: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Setting]: ...

        @overload
        def update(
                self, 
                setting_name: Union[str, SettingNameAutoGenerated], 
                setting: Setting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @overload
        def update(
                self, 
                setting_name: Union[str, SettingNameAutoGenerated], 
                setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...


    class azure.mgmt.security.operations.SoftwareInventoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                software_name: str, 
                **kwargs: Any
            ) -> Software: ...

        @distributed_trace
        def list_by_extended_resource(
                self, 
                resource_group_name: str, 
                resource_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Software]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Software]: ...


    class azure.mgmt.security.operations.SqlVulnerabilityAssessmentBaselineRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def add(
                self, 
                workspace_id: str, 
                resource_id: str, 
                body: Optional[RulesResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RulesResults: ...

        @overload
        def add(
                self, 
                workspace_id: str, 
                resource_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RulesResults: ...

        @overload
        def create_or_update(
                self, 
                rule_id: str, 
                workspace_id: str, 
                resource_id: str, 
                body: Optional[RuleResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuleResults: ...

        @overload
        def create_or_update(
                self, 
                rule_id: str, 
                workspace_id: str, 
                resource_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuleResults: ...

        @distributed_trace
        def delete(
                self, 
                rule_id: str, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                rule_id: str, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> RuleResults: ...

        @distributed_trace
        def list(
                self, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> RulesResults: ...


    class azure.mgmt.security.operations.SqlVulnerabilityAssessmentScanResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scan_id: str, 
                scan_result_id: str, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> ScanResult: ...

        @distributed_trace
        def list(
                self, 
                scan_id: str, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> ScanResults: ...


    class azure.mgmt.security.operations.SqlVulnerabilityAssessmentScansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scan_id: str, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> Scan: ...

        @distributed_trace
        def list(
                self, 
                workspace_id: str, 
                resource_id: str, 
                **kwargs: Any
            ) -> Scans: ...


    class azure.mgmt.security.operations.StandardAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_id: str, 
                standard_assignment_name: str, 
                standard_assignment: StandardAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandardAssignment: ...

        @overload
        def create(
                self, 
                resource_id: str, 
                standard_assignment_name: str, 
                standard_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandardAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_id: str, 
                standard_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_id: str, 
                standard_assignment_name: str, 
                **kwargs: Any
            ) -> StandardAssignment: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[StandardAssignment]: ...


    class azure.mgmt.security.operations.SubAssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                assessment_name: str, 
                sub_assessment_name: str, 
                **kwargs: Any
            ) -> SecuritySubAssessment: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SecuritySubAssessment]: ...

        @distributed_trace
        def list_all(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[SecuritySubAssessment]: ...


    class azure.mgmt.security.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_resource_group_level_task(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                task_name: str, 
                **kwargs: Any
            ) -> SecurityTask: ...

        @distributed_trace
        def get_subscription_level_task(
                self, 
                asc_location: str, 
                task_name: str, 
                **kwargs: Any
            ) -> SecurityTask: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[SecurityTask]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[SecurityTask]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[SecurityTask]: ...

        @distributed_trace
        def update_resource_group_level_task_state(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                task_name: str, 
                task_update_action_type: Union[str, TaskUpdateActionType], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_subscription_level_task_state(
                self, 
                asc_location: str, 
                task_name: str, 
                task_update_action_type: Union[str, TaskUpdateActionType], 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.security.operations.TopologyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                topology_resource_name: str, 
                **kwargs: Any
            ) -> TopologyResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[TopologyResource]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                **kwargs: Any
            ) -> ItemPaged[TopologyResource]: ...


    class azure.mgmt.security.operations.WorkspaceSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                workspace_setting_name: str, 
                workspace_setting: WorkspaceSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceSetting: ...

        @overload
        def create(
                self, 
                workspace_setting_name: str, 
                workspace_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceSetting: ...

        @distributed_trace
        def delete(
                self, 
                workspace_setting_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                workspace_setting_name: str, 
                **kwargs: Any
            ) -> WorkspaceSetting: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[WorkspaceSetting]: ...

        @overload
        def update(
                self, 
                workspace_setting_name: str, 
                workspace_setting: WorkspaceSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceSetting: ...

        @overload
        def update(
                self, 
                workspace_setting_name: str, 
                workspace_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceSetting: ...


```