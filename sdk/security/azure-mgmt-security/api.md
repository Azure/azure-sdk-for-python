```py
namespace azure.mgmt.security

    class azure.mgmt.security.SecurityManagementClient: implements ContextManager 
        advanced_threat_protection: AdvancedThreatProtectionOperations
        alerts: AlertsOperations
        alerts_suppression_rules: AlertsSuppressionRulesOperations
        allowed_connections: AllowedConnectionsOperations
        api_collections: APICollectionsOperations
        application: ApplicationOperations
        applications: ApplicationsOperations
        assessments: AssessmentsOperations
        assessments_metadata: AssessmentsMetadataOperations
        assignments: AssignmentsOperations
        auto_provisioning_settings: AutoProvisioningSettingsOperations
        automations: AutomationsOperations
        azure_dev_ops_orgs: AzureDevOpsOrgsOperations
        azure_dev_ops_projects: AzureDevOpsProjectsOperations
        azure_dev_ops_repos: AzureDevOpsReposOperations
        batch_pricings: BatchPricingsOperations
        compliance_results: ComplianceResultsOperations
        compliances: CompliancesOperations
        custom_recommendations: CustomRecommendationsOperations
        defender_for_storage: DefenderForStorageOperations
        dev_ops_configurations: DevOpsConfigurationsOperations
        dev_ops_operation_results: DevOpsOperationResultsOperations
        device_security_groups: DeviceSecurityGroupsOperations
        discovered_security_solutions: DiscoveredSecuritySolutionsOperations
        external_security_solutions: ExternalSecuritySolutionsOperations
        git_hub_issues: GitHubIssuesOperations
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
        operation_results: OperationResultsOperations
        operation_statuses: OperationStatusesOperations
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
        sql_vulnerability_assessment_baseline_rules: SqlVulnerabilityAssessmentBaselineRulesOperations
        sql_vulnerability_assessment_scan_results: SqlVulnerabilityAssessmentScanResultsOperations
        sql_vulnerability_assessment_scans: SqlVulnerabilityAssessmentScansOperations
        sql_vulnerability_assessment_settings: SqlVulnerabilityAssessmentSettingsOperations
        standard_assignments: StandardAssignmentsOperations
        standards: StandardsOperations
        sub_assessments: SubAssessmentsOperations
        tasks: TasksOperations
        topology: TopologyOperations
        topology_resources: TopologyResourcesOperations
        workspace_settings: WorkspaceSettingsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
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


namespace azure.mgmt.security.aio

    class azure.mgmt.security.aio.SecurityManagementClient: implements AsyncContextManager 
        advanced_threat_protection: AdvancedThreatProtectionOperations
        alerts: AlertsOperations
        alerts_suppression_rules: AlertsSuppressionRulesOperations
        allowed_connections: AllowedConnectionsOperations
        api_collections: APICollectionsOperations
        application: ApplicationOperations
        applications: ApplicationsOperations
        assessments: AssessmentsOperations
        assessments_metadata: AssessmentsMetadataOperations
        assignments: AssignmentsOperations
        auto_provisioning_settings: AutoProvisioningSettingsOperations
        automations: AutomationsOperations
        azure_dev_ops_orgs: AzureDevOpsOrgsOperations
        azure_dev_ops_projects: AzureDevOpsProjectsOperations
        azure_dev_ops_repos: AzureDevOpsReposOperations
        batch_pricings: BatchPricingsOperations
        compliance_results: ComplianceResultsOperations
        compliances: CompliancesOperations
        custom_recommendations: CustomRecommendationsOperations
        defender_for_storage: DefenderForStorageOperations
        dev_ops_configurations: DevOpsConfigurationsOperations
        dev_ops_operation_results: DevOpsOperationResultsOperations
        device_security_groups: DeviceSecurityGroupsOperations
        discovered_security_solutions: DiscoveredSecuritySolutionsOperations
        external_security_solutions: ExternalSecuritySolutionsOperations
        git_hub_issues: GitHubIssuesOperations
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
        operation_results: OperationResultsOperations
        operation_statuses: OperationStatusesOperations
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
        sql_vulnerability_assessment_baseline_rules: SqlVulnerabilityAssessmentBaselineRulesOperations
        sql_vulnerability_assessment_scan_results: SqlVulnerabilityAssessmentScanResultsOperations
        sql_vulnerability_assessment_scans: SqlVulnerabilityAssessmentScansOperations
        sql_vulnerability_assessment_settings: SqlVulnerabilityAssessmentSettingsOperations
        standard_assignments: StandardAssignmentsOperations
        standards: StandardsOperations
        sub_assessments: SubAssessmentsOperations
        tasks: TasksOperations
        topology: TopologyOperations
        topology_resources: TopologyResourcesOperations
        workspace_settings: WorkspaceSettingsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
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
                resource_group_name: str, 
                asc_location: str, 
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
                *, 
                alert_type: Optional[str] = ..., 
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
                *, 
                expand: Optional[Union[str, ExpandEnum]] = ..., 
                **kwargs: Any
            ) -> SecurityAssessmentResponse: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityAssessmentResponse]: ...


    class azure.mgmt.security.aio.operations.AssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                assignment_id: str, 
                assignment: Assignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Assignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                assignment_id: str, 
                assignment: Assignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Assignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                assignment_id: str, 
                assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Assignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                assignment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                assignment_id: str, 
                **kwargs: Any
            ) -> Assignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Assignment]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Assignment]: ...


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


    class azure.mgmt.security.aio.operations.BatchPricingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope_id: str, 
                pricing_batch_name: str, 
                pricing_batch: PricingBatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PricingBatch: ...

        @overload
        async def create_or_update(
                self, 
                scope_id: str, 
                pricing_batch_name: str, 
                pricing_batch: PricingBatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PricingBatch: ...

        @overload
        async def create_or_update(
                self, 
                scope_id: str, 
                pricing_batch_name: str, 
                pricing_batch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PricingBatch: ...

        @distributed_trace_async
        async def get(
                self, 
                scope_id: str, 
                pricing_batch_name: str, 
                **kwargs: Any
            ) -> PricingBatch: ...

        @distributed_trace
        def list(
                self, 
                scope_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PricingBatch]: ...


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
                setting_name: str, 
                scan_id: str, 
                **kwargs: Any
            ) -> MalwareScan: ...

        @overload
        async def create(
                self, 
                resource_id: str, 
                setting_name: str, 
                defender_for_storage_setting: DefenderForStorageSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @overload
        async def create(
                self, 
                resource_id: str, 
                setting_name: str, 
                defender_for_storage_setting: DefenderForStorageSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @overload
        async def create(
                self, 
                resource_id: str, 
                setting_name: str, 
                defender_for_storage_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_id: str, 
                setting_name: str, 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @distributed_trace_async
        async def get_malware_scan(
                self, 
                resource_id: str, 
                setting_name: str, 
                scan_id: str, 
                **kwargs: Any
            ) -> MalwareScan: ...

        @distributed_trace
        def list(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DefenderForStorageSetting]: ...

        @overload
        async def start_malware_scan(
                self, 
                resource_id: str, 
                setting_name: str, 
                body: Optional[StartMalwareScanRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MalwareScan: ...

        @overload
        async def start_malware_scan(
                self, 
                resource_id: str, 
                setting_name: str, 
                body: Optional[StartMalwareScanRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MalwareScan: ...

        @overload
        async def start_malware_scan(
                self, 
                resource_id: str, 
                setting_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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


    class azure.mgmt.security.aio.operations.GitHubIssuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                repo_name: str, 
                create_issue_request: Optional[IssueCreationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                repo_name: str, 
                create_issue_request: Optional[IssueCreationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                repo_name: str, 
                create_issue_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[IoTSecuritySolutionModel]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
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
                *, 
                top: Optional[int] = ..., 
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
                *, 
                top: Optional[int] = ..., 
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


    class azure.mgmt.security.aio.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.security.aio.operations.OperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


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
                *, 
                filter: Optional[str] = ..., 
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
                private_link_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
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
                private_link_name: str, 
                group_id: str, 
                **kwargs: Any
            ) -> PrivateLinkGroupResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkGroupResource]: ...


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
                private_link_name: str, 
                private_link: PrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateLinkResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_link: PrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateLinkResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_link: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateLinkResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace_async
        async def head(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
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
                private_link_name: str, 
                private_link: PrivateLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_link: PrivateLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
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
                *, 
                filter: Optional[str] = ..., 
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
                *, 
                filter: Optional[str] = ..., 
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
                *, 
                filter: Optional[str] = ..., 
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
                *, 
                expand: Optional[Union[str, ExpandControlsEnum]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SecureScoreControlDetails]: ...

        @distributed_trace
        def list_by_secure_score(
                self, 
                secure_score_name: str, 
                *, 
                expand: Optional[Union[str, ExpandControlsEnum]] = ..., 
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

        @distributed_trace
        def list(
                self, 
                pricing_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityOperator]: ...


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
                setting_name: Union[str, SettingName], 
                **kwargs: Any
            ) -> Setting: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Setting]: ...

        @overload
        async def update(
                self, 
                setting_name: Union[str, SettingName], 
                setting: Setting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @overload
        async def update(
                self, 
                setting_name: Union[str, SettingName], 
                setting: Setting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @overload
        async def update(
                self, 
                setting_name: Union[str, SettingName], 
                setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...


    class azure.mgmt.security.aio.operations.SqlVulnerabilityAssessmentBaselineRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add(
                self, 
                resource_id: str, 
                body: Optional[RulesResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RulesResults: ...

        @overload
        async def add(
                self, 
                resource_id: str, 
                body: Optional[RulesResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RulesResults: ...

        @overload
        async def add(
                self, 
                resource_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RulesResults: ...

        @overload
        async def create_or_update(
                self, 
                resource_id: str, 
                rule_id: str, 
                body: Optional[RuleResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleResults: ...

        @overload
        async def create_or_update(
                self, 
                resource_id: str, 
                rule_id: str, 
                body: Optional[RuleResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleResults: ...

        @overload
        async def create_or_update(
                self, 
                resource_id: str, 
                rule_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleResults: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_id: str, 
                rule_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_id: str, 
                rule_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleResults: ...

        @distributed_trace
        def list(
                self, 
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RuleResults]: ...


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
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> ScanResult: ...

        @distributed_trace
        def list(
                self, 
                scan_id: str, 
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ScanResult]: ...


    class azure.mgmt.security.aio.operations.SqlVulnerabilityAssessmentScansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_initiate_scan(
                self, 
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVulnerabilityAssessmentScanOperationResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                scan_id: str, 
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> ScanV2: ...

        @distributed_trace_async
        async def get_scan_operation_result(
                self, 
                resource_id: str, 
                operation_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> SqlVulnerabilityAssessmentScanOperationResult: ...

        @distributed_trace
        def list(
                self, 
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ScanV2]: ...


    class azure.mgmt.security.aio.operations.SqlVulnerabilityAssessmentSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_id: str, 
                body: Optional[SqlVulnerabilityAssessmentSettings] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlVulnerabilityAssessmentSettings: ...

        @overload
        async def create_or_update(
                self, 
                resource_id: str, 
                body: Optional[SqlVulnerabilityAssessmentSettings] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlVulnerabilityAssessmentSettings: ...

        @overload
        async def create_or_update(
                self, 
                resource_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlVulnerabilityAssessmentSettings: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> SqlVulnerabilityAssessmentSettings: ...


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


    class azure.mgmt.security.aio.operations.StandardsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                standard_id: str, 
                standard: Standard, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Standard: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                standard_id: str, 
                standard: Standard, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Standard: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                standard_id: str, 
                standard: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Standard: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                standard_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                standard_id: str, 
                **kwargs: Any
            ) -> Standard: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Standard]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Standard]: ...


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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityTask]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityTask]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                *, 
                filter: Optional[str] = ..., 
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

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[TopologyResource]: ...


    class azure.mgmt.security.aio.operations.TopologyResourcesOperations:

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

    class azure.mgmt.security.models.AadConnectivityStateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCOVERED = "Discovered"
        NOT_LICENSED = "NotLicensed"


    class azure.mgmt.security.models.AadExternalSecuritySolution(ExternalSecuritySolution, discriminator='AAD'):
        id: str
        kind: Literal[ExternalSecuritySolutionKindEnum.AAD]
        location: str
        name: str
        properties: Optional[AadSolutionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AadSolutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AadSolutionProperties(ExternalSecuritySolutionProperties):
        connectivity_state: Optional[Union[str, AadConnectivityStateEnum]]
        device_type: str
        device_vendor: str
        workspace: ConnectedWorkspace

        @overload
        def __init__(
                self, 
                *, 
                connectivity_state: Optional[Union[str, AadConnectivityStateEnum]] = ..., 
                device_type: Optional[str] = ..., 
                device_vendor: Optional[str] = ..., 
                workspace: Optional[ConnectedWorkspace] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AccessTokenAuthentication(Authentication, discriminator='AccessToken'):
        access_token: Optional[str]
        authentication_type: Literal[AuthenticationType.ACCESS_TOKEN]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_token: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_HUB = "EventHub"
        INTERNAL = "Internal"
        LOGIC_APP = "LogicApp"
        WORKSPACE = "Workspace"


    class azure.mgmt.security.models.ActionableRemediation(_Model):
        branch_configuration: Optional[TargetBranchConfiguration]
        category_configurations: Optional[list[CategoryConfiguration]]
        inherit_from_parent_state: Optional[Union[str, InheritFromParentState]]
        state: Optional[Union[str, ActionableRemediationState]]

        @overload
        def __init__(
                self, 
                *, 
                branch_configuration: Optional[TargetBranchConfiguration] = ..., 
                category_configurations: Optional[list[CategoryConfiguration]] = ..., 
                inherit_from_parent_state: Optional[Union[str, InheritFromParentState]] = ..., 
                state: Optional[Union[str, ActionableRemediationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ActionableRemediationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NONE = "None"


    class azure.mgmt.security.models.AdditionalData(_Model):
        assessed_resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                assessed_resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AdditionalWorkspaceDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERTS = "Alerts"
        RAW_EVENTS = "RawEvents"


    class azure.mgmt.security.models.AdditionalWorkspaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SENTINEL = "Sentinel"


    class azure.mgmt.security.models.AdditionalWorkspacesProperties(_Model):
        data_types: Optional[list[Union[str, AdditionalWorkspaceDataType]]]
        type: Optional[Union[str, AdditionalWorkspaceType]]
        workspace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_types: Optional[list[Union[str, AdditionalWorkspaceDataType]]] = ..., 
                type: Optional[Union[str, AdditionalWorkspaceType]] = ..., 
                workspace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AdvancedThreatProtectionProperties(_Model):
        is_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AdvancedThreatProtectionSetting(ExtensionResource):
        id: str
        name: str
        properties: Optional[AdvancedThreatProtectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AdvancedThreatProtectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.AgentlessConfiguration(_Model):
        agentless_auto_discovery: Optional[Union[str, AutoDiscovery]]
        agentless_enabled: Optional[Union[str, AgentlessEnablement]]
        inventory_list: Optional[list[InventoryList]]
        inventory_list_type: Optional[Union[str, InventoryListKind]]
        scanners: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                agentless_auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                agentless_enabled: Optional[Union[str, AgentlessEnablement]] = ..., 
                inventory_list: Optional[list[InventoryList]] = ..., 
                inventory_list_type: Optional[Union[str, InventoryListKind]] = ..., 
                scanners: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AgentlessEnablement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.security.models.Alert(ProxyResource):
        id: str
        name: str
        properties: Optional[AlertProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.AlertEntity(_Model):
        type: Optional[str]


    class azure.mgmt.security.models.AlertProperties(_Model):
        alert_display_name: Optional[str]
        alert_type: Optional[str]
        alert_uri: Optional[str]
        compromised_entity: Optional[str]
        correlation_key: Optional[str]
        description: Optional[str]
        end_time_utc: Optional[datetime]
        entities: Optional[list[AlertEntity]]
        extended_links: Optional[list[dict[str, str]]]
        extended_properties: Optional[dict[str, str]]
        intent: Optional[Union[str, Intent]]
        is_incident: Optional[bool]
        processing_end_time_utc: Optional[datetime]
        product_component_name: Optional[str]
        product_name: Optional[str]
        remediation_steps: Optional[list[str]]
        resource_identifiers: Optional[list[ResourceIdentifier]]
        severity: Optional[Union[str, AlertSeverity]]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, AlertStatus]]
        sub_techniques: Optional[list[str]]
        supporting_evidence: Optional[AlertPropertiesSupportingEvidence]
        system_alert_id: Optional[str]
        techniques: Optional[list[str]]
        time_generated_utc: Optional[datetime]
        vendor_name: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                extended_properties: Optional[dict[str, str]] = ..., 
                supporting_evidence: Optional[AlertPropertiesSupportingEvidence] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AlertPropertiesSupportingEvidence(_Model):
        type: Optional[str]


    class azure.mgmt.security.models.AlertSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        INFORMATIONAL = "Informational"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.AlertSimulatorBundlesRequestProperties(AlertSimulatorRequestProperties, discriminator='Bundles'):
        bundles: Optional[list[Union[str, BundleType]]]
        kind: Literal[KindEnum.BUNDLES]

        @overload
        def __init__(
                self, 
                *, 
                bundles: Optional[list[Union[str, BundleType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AlertSimulatorRequestBody(_Model):
        properties: Optional[AlertSimulatorRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertSimulatorRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AlertSimulatorRequestProperties(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AlertStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DISMISSED = "Dismissed"
        IN_PROGRESS = "InProgress"
        RESOLVED = "Resolved"


    class azure.mgmt.security.models.AlertSyncSettingProperties(_Model):
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AlertSyncSettings(Setting, discriminator='AlertSyncSettings'):
        id: str
        kind: Literal[SettingKind.ALERT_SYNC_SETTINGS]
        name: str
        properties: Optional[AlertSyncSettingProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertSyncSettingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.AlertsSuppressionRule(ProxyResource):
        id: str
        name: str
        properties: Optional[AlertsSuppressionRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertsSuppressionRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.AlertsSuppressionRuleProperties(_Model):
        alert_type: str
        comment: Optional[str]
        expiration_date_utc: Optional[datetime]
        last_modified_utc: Optional[datetime]
        reason: str
        state: Union[str, RuleState]
        suppression_alerts_scope: Optional[SuppressionAlertsScope]

        @overload
        def __init__(
                self, 
                *, 
                alert_type: str, 
                comment: Optional[str] = ..., 
                expiration_date_utc: Optional[datetime] = ..., 
                reason: str, 
                state: Union[str, RuleState], 
                suppression_alerts_scope: Optional[SuppressionAlertsScope] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AllowedConnectionsResource(ProxyResource):
        id: str
        location: str
        name: str
        properties: Optional[AllowedConnectionsResourceProperties]
        system_data: SystemData
        type: str


    class azure.mgmt.security.models.AllowedConnectionsResourceProperties(_Model):
        calculated_date_time: Optional[datetime]
        connectable_resources: Optional[list[ConnectableResource]]


    class azure.mgmt.security.models.AllowlistCustomAlertRule(ListCustomAlertRule, discriminator='AllowlistCustomAlertRule'):
        allowlist_values: list[str]
        description: str
        display_name: str
        is_enabled: bool
        rule_type: Literal["AllowlistCustomAlertRule"]
        value_type: Union[str, ValueType]

        @overload
        def __init__(
                self, 
                *, 
                allowlist_values: list[str], 
                is_enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AnnotateDefaultBranchState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.ApiCollection(ExtensionResource):
        id: str
        name: str
        properties: Optional[ApiCollectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ApiCollectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.ApiCollectionProperties(_Model):
        base_url: Optional[str]
        discovered_via: Optional[str]
        display_name: Optional[str]
        number_of_api_endpoints: Optional[int]
        number_of_api_endpoints_with_sensitive_data_exposed: Optional[int]
        number_of_external_api_endpoints: Optional[int]
        number_of_inactive_api_endpoints: Optional[int]
        number_of_unauthenticated_api_endpoints: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        sensitivity_label: Optional[str]


    class azure.mgmt.security.models.Application(ProxyResource):
        id: str
        name: str
        properties: Optional[ApplicationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ApplicationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.ApplicationProperties(_Model):
        condition_sets: list[Any]
        description: Optional[str]
        display_name: Optional[str]
        source_resource_type: Union[str, ApplicationSourceResourceType]

        @overload
        def __init__(
                self, 
                *, 
                condition_sets: list[Any], 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                source_resource_type: Union[str, ApplicationSourceResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ApplicationSourceResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSESSMENTS = "Assessments"


    class azure.mgmt.security.models.ArcAutoProvisioning(_Model):
        configuration: Optional[ArcAutoProvisioningConfiguration]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ArcAutoProvisioningAws(ArcAutoProvisioning):
        cloud_role_arn: Optional[str]
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ArcAutoProvisioningConfiguration(_Model):
        private_link_scope: Optional[str]
        proxy: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_link_scope: Optional[str] = ..., 
                proxy: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ArcAutoProvisioningGcp(ArcAutoProvisioning):
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ArmActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.security.models.AscLocation(ProxyResource):
        id: str
        name: str
        properties: Optional[Any]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.AssessedResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_REGISTRY_VULNERABILITY = "ContainerRegistryVulnerability"
        SERVER_VULNERABILITY = "ServerVulnerability"
        SERVER_VULNERABILITY_ASSESSMENT = "ServerVulnerabilityAssessment"
        SQL_SERVER_VULNERABILITY = "SqlServerVulnerability"


    class azure.mgmt.security.models.AssessmentLinks(_Model):
        azure_portal_uri: Optional[str]


    class azure.mgmt.security.models.AssessmentStatus(_Model):
        cause: Optional[str]
        code: Union[str, AssessmentStatusCode]
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cause: Optional[str] = ..., 
                code: Union[str, AssessmentStatusCode], 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AssessmentStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_APPLICABLE = "NotApplicable"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.security.models.AssessmentStatusResponse(AssessmentStatus):
        cause: str
        code: Union[str, AssessmentStatusCode]
        description: str
        first_evaluation_date: Optional[datetime]
        status_change_date: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                cause: Optional[str] = ..., 
                code: Union[str, AssessmentStatusCode], 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AssessmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN = "BuiltIn"
        BUILT_IN_POLICY = "BuiltInPolicy"
        CUSTOM = "Custom"
        CUSTOMER_MANAGED = "CustomerManaged"
        CUSTOM_POLICY = "CustomPolicy"
        DYNAMIC_BUILT_IN = "DynamicBuiltIn"
        MANUAL_BUILT_IN = "ManualBuiltIn"
        MANUAL_BUILT_IN_POLICY = "ManualBuiltInPolicy"
        MANUAL_CUSTOM_POLICY = "ManualCustomPolicy"
        UNKNOWN = "Unknown"
        VERIFIED_PARTNER = "VerifiedPartner"


    class azure.mgmt.security.models.AssignedAssessmentItem(_Model):
        assessment_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assessment_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AssignedComponentItem(_Model):
        key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AssignedStandardItem(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.Assignment(ProxyResource):
        etag: Optional[str]
        id: str
        kind: Optional[str]
        location: Optional[str]
        name: str
        properties: Optional[AssignmentProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[AssignmentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.AssignmentProperties(_Model):
        additional_data: Optional[AssignmentPropertiesAdditionalData]
        assigned_component: Optional[AssignedComponentItem]
        assigned_standard: Optional[AssignedStandardItem]
        description: Optional[str]
        display_name: Optional[str]
        effect: Optional[str]
        expires_on: Optional[datetime]
        metadata: Optional[Any]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_data: Optional[AssignmentPropertiesAdditionalData] = ..., 
                assigned_component: Optional[AssignedComponentItem] = ..., 
                assigned_standard: Optional[AssignedStandardItem] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                effect: Optional[str] = ..., 
                expires_on: Optional[datetime] = ..., 
                metadata: Optional[Any] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AssignmentPropertiesAdditionalData(_Model):
        exemption_category: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                exemption_category: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AtaExternalSecuritySolution(ExternalSecuritySolution, discriminator='ATA'):
        id: str
        kind: Literal[ExternalSecuritySolutionKindEnum.ATA]
        location: str
        name: str
        properties: Optional[AtaSolutionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AtaSolutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AtaSolutionProperties(ExternalSecuritySolutionProperties):
        device_type: str
        device_vendor: str
        last_event_received: Optional[str]
        workspace: ConnectedWorkspace

        @overload
        def __init__(
                self, 
                *, 
                device_type: Optional[str] = ..., 
                device_vendor: Optional[str] = ..., 
                last_event_received: Optional[str] = ..., 
                workspace: Optional[ConnectedWorkspace] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AttestationComplianceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANT = "compliant"
        NON_COMPLIANT = "nonCompliant"
        UNKNOWN = "unknown"


    class azure.mgmt.security.models.AttestationEvidence(_Model):
        description: Optional[str]
        source_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                source_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.Authentication(_Model):
        authentication_type: str

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_TOKEN = "AccessToken"


    class azure.mgmt.security.models.Authorization(_Model):
        code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutoDiscovery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.security.models.AutoProvision(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.security.models.AutoProvisioningSetting(ProxyResource):
        id: str
        name: str
        properties: Optional[AutoProvisioningSettingProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutoProvisioningSettingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.AutoProvisioningSettingProperties(_Model):
        auto_provision: Union[str, AutoProvision]

        @overload
        def __init__(
                self, 
                *, 
                auto_provision: Union[str, AutoProvision]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutomatedResponseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_SOFT_DELETE = "BlobSoftDelete"
        NONE = "None"


    class azure.mgmt.security.models.Automation(ProxyResource):
        etag: Optional[str]
        id: str
        kind: Optional[str]
        location: Optional[str]
        name: str
        properties: Optional[AutomationProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[AutomationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.AutomationAction(_Model):
        action_type: str

        @overload
        def __init__(
                self, 
                *, 
                action_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutomationActionEventHub(AutomationAction, discriminator='EventHub'):
        action_type: Literal[ActionType.EVENT_HUB]
        connection_string: Optional[str]
        event_hub_resource_id: Optional[str]
        is_trusted_service_enabled: Optional[bool]
        sas_policy_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_string: Optional[str] = ..., 
                event_hub_resource_id: Optional[str] = ..., 
                is_trusted_service_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutomationActionLogicApp(AutomationAction, discriminator='LogicApp'):
        action_type: Literal[ActionType.LOGIC_APP]
        logic_app_resource_id: Optional[str]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                logic_app_resource_id: Optional[str] = ..., 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutomationActionWorkspace(AutomationAction, discriminator='Workspace'):
        action_type: Literal[ActionType.WORKSPACE]
        workspace_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                workspace_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutomationProperties(_Model):
        actions: Optional[list[AutomationAction]]
        description: Optional[str]
        is_enabled: Optional[bool]
        scopes: Optional[list[AutomationScope]]
        sources: Optional[list[AutomationSource]]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[AutomationAction]] = ..., 
                description: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                scopes: Optional[list[AutomationScope]] = ..., 
                sources: Optional[list[AutomationSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutomationRuleSet(_Model):
        rules: Optional[list[AutomationTriggeringRule]]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[list[AutomationTriggeringRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutomationScope(_Model):
        description: Optional[str]
        scope_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                scope_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutomationSource(_Model):
        event_source: Optional[Union[str, EventSource]]
        rule_sets: Optional[list[AutomationRuleSet]]

        @overload
        def __init__(
                self, 
                *, 
                event_source: Optional[Union[str, EventSource]] = ..., 
                rule_sets: Optional[list[AutomationRuleSet]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutomationTriggeringRule(_Model):
        expected_value: Optional[str]
        operator: Optional[Union[str, Operator]]
        property_j_path: Optional[str]
        property_type: Optional[Union[str, PropertyType]]

        @overload
        def __init__(
                self, 
                *, 
                expected_value: Optional[str] = ..., 
                operator: Optional[Union[str, Operator]] = ..., 
                property_j_path: Optional[str] = ..., 
                property_type: Optional[Union[str, PropertyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AutomationUpdateModel(Tags):
        properties: Optional[AutomationProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutomationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.AutomationValidationStatus(_Model):
        is_valid: Optional[bool]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_valid: Optional[bool] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AwsCloudTrailConfiguration(_Model):
        cloud_trail_resource_sets: Optional[list[AwsCloudTrailResourceSet]]
        deployment_region: Optional[str]
        provisioning_type: Optional[Union[str, AwsCloudTrailProvisioningType]]
        resource_name_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_trail_resource_sets: Optional[list[AwsCloudTrailResourceSet]] = ..., 
                deployment_region: Optional[str] = ..., 
                provisioning_type: Optional[Union[str, AwsCloudTrailProvisioningType]] = ..., 
                resource_name_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AwsCloudTrailProvisioningType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_PROVISIONING = "AutoProvisioning"
        BRING_YOUR_OWN = "BringYourOwn"
        MANUAL_PROVISIONING = "ManualProvisioning"


    class azure.mgmt.security.models.AwsCloudTrailResourceSet(_Model):
        kms_key_arn: Optional[str]
        resource_region: Optional[str]
        s3_bucket_arn: Optional[str]
        sqs_queue_arn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kms_key_arn: Optional[str] = ..., 
                resource_region: Optional[str] = ..., 
                s3_bucket_arn: Optional[str] = ..., 
                sqs_queue_arn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AwsEnvironmentData(EnvironmentData, discriminator='AwsAccount'):
        account_name: Optional[str]
        environment_type: Literal[EnvironmentType.AWS_ACCOUNT]
        organizational_data: Optional[AwsOrganizationalData]
        regions: Optional[list[str]]
        scan_interval: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                organizational_data: Optional[AwsOrganizationalData] = ..., 
                regions: Optional[list[str]] = ..., 
                scan_interval: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AwsOrganizationalData(_Model):
        organization_membership_type: str

        @overload
        def __init__(
                self, 
                *, 
                organization_membership_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AwsOrganizationalDataMaster(AwsOrganizationalData, discriminator='Organization'):
        excluded_account_ids: Optional[list[str]]
        organization_membership_type: Literal[OrganizationMembershipType.ORGANIZATION]
        stackset_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                excluded_account_ids: Optional[list[str]] = ..., 
                stackset_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AwsOrganizationalDataMember(AwsOrganizationalData, discriminator='Member'):
        organization_membership_type: Literal[OrganizationMembershipType.MEMBER]
        parent_hierarchy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                parent_hierarchy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureDevOpsOrg(ProxyResource):
        id: str
        name: str
        properties: Optional[AzureDevOpsOrgProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureDevOpsOrgProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureDevOpsOrgListResponse(_Model):
        next_link: Optional[str]
        value: Optional[list[AzureDevOpsOrg]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[AzureDevOpsOrg]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureDevOpsOrgProperties(_Model):
        actionable_remediation: Optional[ActionableRemediation]
        onboarding_state: Optional[Union[str, OnboardingState]]
        provisioning_state: Optional[Union[str, DevOpsProvisioningState]]
        provisioning_status_message: Optional[str]
        provisioning_status_update_time_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                actionable_remediation: Optional[ActionableRemediation] = ..., 
                onboarding_state: Optional[Union[str, OnboardingState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureDevOpsProject(ProxyResource):
        id: str
        name: str
        properties: Optional[AzureDevOpsProjectProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureDevOpsProjectProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureDevOpsProjectProperties(_Model):
        actionable_remediation: Optional[ActionableRemediation]
        onboarding_state: Optional[Union[str, OnboardingState]]
        parent_org_name: Optional[str]
        project_id: Optional[str]
        provisioning_state: Optional[Union[str, DevOpsProvisioningState]]
        provisioning_status_message: Optional[str]
        provisioning_status_update_time_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                actionable_remediation: Optional[ActionableRemediation] = ..., 
                onboarding_state: Optional[Union[str, OnboardingState]] = ..., 
                parent_org_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureDevOpsRepository(ProxyResource):
        id: str
        name: str
        properties: Optional[AzureDevOpsRepositoryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureDevOpsRepositoryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureDevOpsRepositoryProperties(_Model):
        actionable_remediation: Optional[ActionableRemediation]
        onboarding_state: Optional[Union[str, OnboardingState]]
        parent_org_name: Optional[str]
        parent_project_name: Optional[str]
        provisioning_state: Optional[Union[str, DevOpsProvisioningState]]
        provisioning_status_message: Optional[str]
        provisioning_status_update_time_utc: Optional[datetime]
        repo_id: Optional[str]
        repo_url: Optional[str]
        visibility: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actionable_remediation: Optional[ActionableRemediation] = ..., 
                onboarding_state: Optional[Union[str, OnboardingState]] = ..., 
                parent_org_name: Optional[str] = ..., 
                parent_project_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureDevOpsScopeEnvironmentData(EnvironmentData, discriminator='AzureDevOpsScope'):
        environment_type: Literal[EnvironmentType.AZURE_DEV_OPS_SCOPE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureResourceDetails(CommonResourceDetails, discriminator='Azure'):
        id: Optional[str]
        source: Literal[Source.AZURE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureResourceIdentifier(ResourceIdentifier, discriminator='AzureResource'):
        azure_resource_id: Optional[str]
        type: Literal[ResourceIdentifierType.AZURE_RESOURCE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.AzureResourceLink(_Model):
        id: Optional[str]


    class azure.mgmt.security.models.AzureServersSetting(ServerVulnerabilityAssessmentsSetting, discriminator='AzureServersSetting'):
        id: str
        kind: Literal[ServerVulnerabilityAssessmentsSettingKind.AZURE_SERVERS_SETTING]
        name: str
        properties: Optional[ServerVulnerabilityAssessmentsAzureSettingProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServerVulnerabilityAssessmentsAzureSettingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.Baseline(_Model):
        expected_results: Optional[list[list[str]]]
        updated_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                expected_results: Optional[list[list[str]]] = ..., 
                updated_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.BaselineAdjustedResult(_Model):
        baseline: Optional[Baseline]
        results_not_in_baseline: Optional[list[list[str]]]
        results_only_in_baseline: Optional[list[list[str]]]
        status: Optional[Union[str, RuleStatus]]

        @overload
        def __init__(
                self, 
                *, 
                baseline: Optional[Baseline] = ..., 
                results_not_in_baseline: Optional[list[list[str]]] = ..., 
                results_only_in_baseline: Optional[list[list[str]]] = ..., 
                status: Optional[Union[str, RuleStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.BenchmarkReference(_Model):
        benchmark: Optional[str]
        reference: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                benchmark: Optional[str] = ..., 
                reference: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.BlobScanFilter(_Model):
        blob: Optional[MatchFilter]
        container: Optional[MatchFilter]

        @overload
        def __init__(
                self, 
                *, 
                blob: Optional[MatchFilter] = ..., 
                container: Optional[MatchFilter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.BlobScanResultsOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_INDEX_TAGS = "BlobIndexTags"
        NONE = "None"


    class azure.mgmt.security.models.BlobsScanSummary(_Model):
        failed_blobs_count: Optional[int]
        malicious_blobs_count: Optional[int]
        scanned_blobs_in_gb: Optional[float]
        skipped_blobs_count: Optional[int]
        total_blobs_scanned: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                failed_blobs_count: Optional[int] = ..., 
                malicious_blobs_count: Optional[int] = ..., 
                scanned_blobs_in_gb: Optional[float] = ..., 
                skipped_blobs_count: Optional[int] = ..., 
                total_blobs_scanned: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.BuiltInInfoType(_Model):
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.security.models.CVE(_Model):
        link: Optional[str]
        title: Optional[str]


    class azure.mgmt.security.models.CVSS(_Model):
        base: Optional[float]


    class azure.mgmt.security.models.Categories(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP_SERVICES = "AppServices"
        COMPUTE = "Compute"
        CONTAINER = "Container"
        DATA = "Data"
        IDENTITY_AND_ACCESS = "IdentityAndAccess"
        IO_T = "IoT"
        NETWORKING = "Networking"


    class azure.mgmt.security.models.CategoryConfiguration(_Model):
        category: Optional[Union[str, RuleCategory]]
        minimum_severity_level: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, RuleCategory]] = ..., 
                minimum_severity_level: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CefExternalSecuritySolution(ExternalSecuritySolution, discriminator='CEF'):
        id: str
        kind: Literal[ExternalSecuritySolutionKindEnum.CEF]
        location: str
        name: str
        properties: Optional[CefSolutionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CefSolutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CefSolutionProperties(ExternalSecuritySolutionProperties):
        agent: Optional[str]
        device_type: str
        device_vendor: str
        hostname: Optional[str]
        last_event_received: Optional[str]
        workspace: ConnectedWorkspace

        @overload
        def __init__(
                self, 
                *, 
                agent: Optional[str] = ..., 
                device_type: Optional[str] = ..., 
                device_vendor: Optional[str] = ..., 
                hostname: Optional[str] = ..., 
                last_event_received: Optional[str] = ..., 
                workspace: Optional[ConnectedWorkspace] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.CloudErrorBody(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[CloudErrorBody]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.security.models.CloudName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "AWS"
        AZURE = "Azure"
        AZURE_DEV_OPS = "AzureDevOps"
        DOCKER_HUB = "DockerHub"
        GCP = "GCP"
        GITHUB = "Github"
        GIT_LAB = "GitLab"
        J_FROG = "JFrog"


    class azure.mgmt.security.models.CloudOffering(_Model):
        description: Optional[str]
        offering_type: str

        @overload
        def __init__(
                self, 
                *, 
                offering_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CommonResourceDetails(_Model):
        source: str

        @overload
        def __init__(
                self, 
                *, 
                source: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.Compliance(ExtensionResource):
        id: str
        name: str
        properties: Optional[ComplianceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ComplianceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.ComplianceProperties(_Model):
        assessment_result: Optional[list[ComplianceSegment]]
        assessment_timestamp_utc_date: Optional[datetime]
        resource_count: Optional[int]


    class azure.mgmt.security.models.ComplianceResult(ExtensionResource):
        id: str
        name: str
        properties: Optional[ComplianceResultProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ComplianceResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.ComplianceResultProperties(_Model):
        resource_status: Optional[Union[str, ResourceStatus]]


    class azure.mgmt.security.models.ComplianceSegment(_Model):
        percentage: Optional[float]
        segment_type: Optional[str]


    class azure.mgmt.security.models.ConnectableResource(_Model):
        id: Optional[str]
        inbound_connected_resources: Optional[list[ConnectedResource]]
        outbound_connected_resources: Optional[list[ConnectedResource]]


    class azure.mgmt.security.models.ConnectedResource(_Model):
        connected_resource_id: Optional[str]
        tcp_ports: Optional[str]
        udp_ports: Optional[str]


    class azure.mgmt.security.models.ConnectedWorkspace(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        INTERNAL = "Internal"


    class azure.mgmt.security.models.ContainerRegistryVulnerabilityProperties(AdditionalData, discriminator='ContainerRegistryVulnerability'):
        assessed_resource_type: Literal[AssessedResourceType.CONTAINER_REGISTRY_VULNERABILITY]
        cve: Optional[list[_models.CVE]]
        cvss: Optional[dict[str, _models.CVSS]]
        image_digest: Optional[str]
        patchable: Optional[bool]
        published_time: Optional[datetime]
        repository_name: Optional[str]
        type: Optional[str]
        vendor_references: Optional[list[VendorReference]]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ControlType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN = "BuiltIn"
        CUSTOM = "Custom"


    class azure.mgmt.security.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.security.models.CspmMonitorAwsOffering(CloudOffering, discriminator='CspmMonitorAws'):
        description: str
        native_cloud_connection: Optional[CspmMonitorAwsOfferingNativeCloudConnection]
        offering_type: Literal[OfferingType.CSPM_MONITOR_AWS]

        @overload
        def __init__(
                self, 
                *, 
                native_cloud_connection: Optional[CspmMonitorAwsOfferingNativeCloudConnection] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CspmMonitorAwsOfferingNativeCloudConnection(_Model):
        cloud_role_arn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CspmMonitorAzureDevOpsOffering(CloudOffering, discriminator='CspmMonitorAzureDevOps'):
        description: str
        offering_type: Literal[OfferingType.CSPM_MONITOR_AZURE_DEV_OPS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CspmMonitorDockerHubOffering(CloudOffering, discriminator='CspmMonitorDockerHub'):
        description: str
        offering_type: Literal[OfferingType.CSPM_MONITOR_DOCKER_HUB]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CspmMonitorGcpOffering(CloudOffering, discriminator='CspmMonitorGcp'):
        description: str
        native_cloud_connection: Optional[CspmMonitorGcpOfferingNativeCloudConnection]
        offering_type: Literal[OfferingType.CSPM_MONITOR_GCP]

        @overload
        def __init__(
                self, 
                *, 
                native_cloud_connection: Optional[CspmMonitorGcpOfferingNativeCloudConnection] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CspmMonitorGcpOfferingNativeCloudConnection(_Model):
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CspmMonitorGitLabOffering(CloudOffering, discriminator='CspmMonitorGitLab'):
        description: str
        offering_type: Literal[OfferingType.CSPM_MONITOR_GIT_LAB]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CspmMonitorGithubOffering(CloudOffering, discriminator='CspmMonitorGithub'):
        description: str
        offering_type: Literal[OfferingType.CSPM_MONITOR_GITHUB]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CspmMonitorJFrogOffering(CloudOffering, discriminator='CspmMonitorJFrog'):
        description: str
        offering_type: Literal[OfferingType.CSPM_MONITOR_J_FROG]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CustomAlertRule(_Model):
        description: Optional[str]
        display_name: Optional[str]
        is_enabled: bool
        rule_type: str

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                rule_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.CustomRecommendation(ExtensionResource):
        id: str
        name: str
        properties: Optional[CustomRecommendationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CustomRecommendationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.CustomRecommendationProperties(_Model):
        assessment_key: Optional[str]
        cloud_providers: Optional[list[Union[str, RecommendationSupportedClouds]]]
        description: Optional[str]
        display_name: Optional[str]
        query: Optional[str]
        remediation_description: Optional[str]
        security_issue: Optional[Union[str, SecurityIssue]]
        severity: Optional[Union[str, SeverityEnum]]

        @overload
        def __init__(
                self, 
                *, 
                cloud_providers: Optional[list[Union[str, RecommendationSupportedClouds]]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                query: Optional[str] = ..., 
                remediation_description: Optional[str] = ..., 
                security_issue: Optional[Union[str, SecurityIssue]] = ..., 
                severity: Optional[Union[str, SeverityEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DataExportSettingProperties(_Model):
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DataExportSettings(Setting, discriminator='DataExportSettings'):
        id: str
        kind: Literal[SettingKind.DATA_EXPORT_SETTINGS]
        name: str
        properties: Optional[DataExportSettingProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DataExportSettingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.DataSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TWIN_DATA = "TwinData"


    class azure.mgmt.security.models.DefenderCspmAwsOffering(CloudOffering, discriminator='DefenderCspmAws'):
        agentless_serverless_posture: Optional[DefenderCspmAwsOfferingAgentlessServerlessPosture]
        ciem: Optional[DefenderCspmAwsOfferingCiem]
        data_sensitivity_discovery: Optional[DefenderCspmAwsOfferingDataSensitivityDiscovery]
        databases_dspm: Optional[DefenderCspmAwsOfferingDatabasesDspm]
        description: str
        mdc_containers_agentless_discovery_k8_s: Optional[DefenderCspmAwsOfferingMdcContainersAgentlessDiscoveryK8S]
        mdc_containers_image_assessment: Optional[DefenderCspmAwsOfferingMdcContainersImageAssessment]
        offering_type: Literal[OfferingType.DEFENDER_CSPM_AWS]
        serverless_containers: Optional[DefenderCspmAwsOfferingServerlessContainers]
        vm_scanners: Optional[DefenderCspmAwsOfferingVmScanners]

        @overload
        def __init__(
                self, 
                *, 
                agentless_serverless_posture: Optional[DefenderCspmAwsOfferingAgentlessServerlessPosture] = ..., 
                ciem: Optional[DefenderCspmAwsOfferingCiem] = ..., 
                data_sensitivity_discovery: Optional[DefenderCspmAwsOfferingDataSensitivityDiscovery] = ..., 
                databases_dspm: Optional[DefenderCspmAwsOfferingDatabasesDspm] = ..., 
                mdc_containers_agentless_discovery_k8_s: Optional[DefenderCspmAwsOfferingMdcContainersAgentlessDiscoveryK8S] = ..., 
                mdc_containers_image_assessment: Optional[DefenderCspmAwsOfferingMdcContainersImageAssessment] = ..., 
                serverless_containers: Optional[DefenderCspmAwsOfferingServerlessContainers] = ..., 
                vm_scanners: Optional[DefenderCspmAwsOfferingVmScanners] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingAgentlessServerlessPosture(_Model):
        cloud_role_arn: Optional[str]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingCiem(_Model):
        ciem_oidc: Optional[DefenderCspmAwsOfferingCiemOidc]
        cloud_trail_audit_log_ingestion: Optional[AwsCloudTrailConfiguration]
        log_collection_oidc: Optional[DefenderCspmAwsOfferingCiemLogCollectionOidc]

        @overload
        def __init__(
                self, 
                *, 
                ciem_oidc: Optional[DefenderCspmAwsOfferingCiemOidc] = ..., 
                cloud_trail_audit_log_ingestion: Optional[AwsCloudTrailConfiguration] = ..., 
                log_collection_oidc: Optional[DefenderCspmAwsOfferingCiemLogCollectionOidc] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingCiemLogCollectionOidc(_Model):
        cloud_role_arn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingCiemOidc(_Model):
        azure_active_directory_app_name: Optional[str]
        cloud_role_arn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_active_directory_app_name: Optional[str] = ..., 
                cloud_role_arn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingDataSensitivityDiscovery(_Model):
        cloud_role_arn: Optional[str]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingDatabasesDspm(_Model):
        cloud_role_arn: Optional[str]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingMdcContainersAgentlessDiscoveryK8S(_Model):
        cloud_role_arn: Optional[str]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingMdcContainersImageAssessment(_Model):
        cloud_role_arn: Optional[str]
        enabled: Optional[bool]
        security_findings_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                security_findings_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingServerlessContainers(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmAwsOfferingVmScanners(VmScannersAws):
        cloud_role_arn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmDockerHubOffering(CloudOffering, discriminator='DefenderCspmDockerHub'):
        description: str
        offering_type: Literal[OfferingType.DEFENDER_CSPM_DOCKER_HUB]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmGcpOffering(CloudOffering, discriminator='DefenderCspmGcp'):
        ciem: Optional[DefenderCspmGcpOfferingCiem]
        ciem_discovery: Optional[DefenderCspmGcpOfferingCiemDiscovery]
        data_sensitivity_discovery: Optional[DefenderCspmGcpOfferingDataSensitivityDiscovery]
        description: str
        mdc_containers_agentless_discovery_k8_s: Optional[DefenderCspmGcpOfferingMdcContainersAgentlessDiscoveryK8S]
        mdc_containers_image_assessment: Optional[DefenderCspmGcpOfferingMdcContainersImageAssessment]
        offering_type: Literal[OfferingType.DEFENDER_CSPM_GCP]
        vm_scanners: Optional[DefenderCspmGcpOfferingVmScanners]

        @overload
        def __init__(
                self, 
                *, 
                ciem: Optional[DefenderCspmGcpOfferingCiem] = ..., 
                ciem_discovery: Optional[DefenderCspmGcpOfferingCiemDiscovery] = ..., 
                data_sensitivity_discovery: Optional[DefenderCspmGcpOfferingDataSensitivityDiscovery] = ..., 
                mdc_containers_agentless_discovery_k8_s: Optional[DefenderCspmGcpOfferingMdcContainersAgentlessDiscoveryK8S] = ..., 
                mdc_containers_image_assessment: Optional[DefenderCspmGcpOfferingMdcContainersImageAssessment] = ..., 
                vm_scanners: Optional[DefenderCspmGcpOfferingVmScanners] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingCiem(_Model):
        ciem_oidc: Optional[DefenderCspmGcpOfferingCiemOidc]
        gcp_audit_log_ingestion: Optional[GcpAuditLogConfiguration]
        log_collection_oidc: Optional[DefenderCspmGcpOfferingCiemOidc]

        @overload
        def __init__(
                self, 
                *, 
                ciem_oidc: Optional[DefenderCspmGcpOfferingCiemOidc] = ..., 
                gcp_audit_log_ingestion: Optional[GcpAuditLogConfiguration] = ..., 
                log_collection_oidc: Optional[DefenderCspmGcpOfferingCiemOidc] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingCiemDiscovery(_Model):
        azure_active_directory_app_name: Optional[str]
        enable_audit_log_ingestion: Optional[bool]
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_active_directory_app_name: Optional[str] = ..., 
                enable_audit_log_ingestion: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingCiemOidc(_Model):
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingDataSensitivityDiscovery(_Model):
        enabled: Optional[bool]
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingMdcContainersAgentlessDiscoveryK8S(_Model):
        enabled: Optional[bool]
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingMdcContainersImageAssessment(_Model):
        enabled: Optional[bool]
        security_findings_enabled: Optional[bool]
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                security_findings_enabled: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmGcpOfferingVmScanners(VmScannersGcp):
        configuration: VmScannersBaseConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmJFrogOffering(CloudOffering, discriminator='DefenderCspmJFrog'):
        description: str
        mdc_containers_image_assessment: Optional[DefenderCspmJFrogOfferingMdcContainersImageAssessment]
        offering_type: Literal[OfferingType.DEFENDER_CSPM_J_FROG]

        @overload
        def __init__(
                self, 
                *, 
                mdc_containers_image_assessment: Optional[DefenderCspmJFrogOfferingMdcContainersImageAssessment] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderCspmJFrogOfferingMdcContainersImageAssessment(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderFoDatabasesAwsOffering(CloudOffering, discriminator='DefenderForDatabasesAws'):
        arc_auto_provisioning: Optional[DefenderFoDatabasesAwsOfferingArcAutoProvisioning]
        databases_dspm: Optional[DefenderFoDatabasesAwsOfferingDatabasesDspm]
        description: str
        offering_type: Literal[OfferingType.DEFENDER_FOR_DATABASES_AWS]
        rds: Optional[DefenderFoDatabasesAwsOfferingRds]

        @overload
        def __init__(
                self, 
                *, 
                arc_auto_provisioning: Optional[DefenderFoDatabasesAwsOfferingArcAutoProvisioning] = ..., 
                databases_dspm: Optional[DefenderFoDatabasesAwsOfferingDatabasesDspm] = ..., 
                rds: Optional[DefenderFoDatabasesAwsOfferingRds] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderFoDatabasesAwsOfferingArcAutoProvisioning(ArcAutoProvisioningAws):
        cloud_role_arn: str
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderFoDatabasesAwsOfferingDatabasesDspm(_Model):
        cloud_role_arn: Optional[str]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderFoDatabasesAwsOfferingRds(_Model):
        cloud_role_arn: Optional[str]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOffering(CloudOffering, discriminator='DefenderForContainersAws'):
        cloud_watch_to_kinesis: Optional[DefenderForContainersAwsOfferingCloudWatchToKinesis]
        container_anti_malware_enabled: Optional[bool]
        data_collection_external_id: Optional[str]
        description: str
        enable_audit_logs_auto_provisioning: Optional[bool]
        enable_defender_agent_auto_provisioning: Optional[bool]
        enable_policy_agent_auto_provisioning: Optional[bool]
        installation_method: Optional[Union[str, InstallationMethod]]
        kinesis_to_s3: Optional[DefenderForContainersAwsOfferingKinesisToS3]
        kube_audit_retention_time: Optional[int]
        kubernetes_data_collection: Optional[DefenderForContainersAwsOfferingKubernetesDataCollection]
        kubernetes_service: Optional[DefenderForContainersAwsOfferingKubernetesService]
        mdc_containers_agentless_discovery_k8_s: Optional[DefenderForContainersAwsOfferingMdcContainersAgentlessDiscoveryK8S]
        mdc_containers_image_assessment: Optional[DefenderForContainersAwsOfferingMdcContainersImageAssessment]
        offering_type: Literal[OfferingType.DEFENDER_FOR_CONTAINERS_AWS]
        security_gating_enabled: Optional[bool]
        vm_scanners: Optional[DefenderForContainersAwsOfferingVmScanners]

        @overload
        def __init__(
                self, 
                *, 
                cloud_watch_to_kinesis: Optional[DefenderForContainersAwsOfferingCloudWatchToKinesis] = ..., 
                container_anti_malware_enabled: Optional[bool] = ..., 
                data_collection_external_id: Optional[str] = ..., 
                enable_audit_logs_auto_provisioning: Optional[bool] = ..., 
                enable_defender_agent_auto_provisioning: Optional[bool] = ..., 
                enable_policy_agent_auto_provisioning: Optional[bool] = ..., 
                installation_method: Optional[Union[str, InstallationMethod]] = ..., 
                kinesis_to_s3: Optional[DefenderForContainersAwsOfferingKinesisToS3] = ..., 
                kube_audit_retention_time: Optional[int] = ..., 
                kubernetes_data_collection: Optional[DefenderForContainersAwsOfferingKubernetesDataCollection] = ..., 
                kubernetes_service: Optional[DefenderForContainersAwsOfferingKubernetesService] = ..., 
                mdc_containers_agentless_discovery_k8_s: Optional[DefenderForContainersAwsOfferingMdcContainersAgentlessDiscoveryK8S] = ..., 
                mdc_containers_image_assessment: Optional[DefenderForContainersAwsOfferingMdcContainersImageAssessment] = ..., 
                security_gating_enabled: Optional[bool] = ..., 
                vm_scanners: Optional[DefenderForContainersAwsOfferingVmScanners] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingCloudWatchToKinesis(_Model):
        cloud_role_arn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingKinesisToS3(_Model):
        cloud_role_arn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingKubernetesDataCollection(_Model):
        cloud_role_arn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingKubernetesService(_Model):
        cloud_role_arn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingMdcContainersAgentlessDiscoveryK8S(_Model):
        cloud_role_arn: Optional[str]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingMdcContainersImageAssessment(_Model):
        cloud_role_arn: Optional[str]
        enabled: Optional[bool]
        security_findings_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                security_findings_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersAwsOfferingVmScanners(VmScannersAws):
        cloud_role_arn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersDockerHubOffering(CloudOffering, discriminator='DefenderForContainersDockerHub'):
        description: str
        offering_type: Literal[OfferingType.DEFENDER_FOR_CONTAINERS_DOCKER_HUB]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOffering(CloudOffering, discriminator='DefenderForContainersGcp'):
        container_anti_malware_enabled: Optional[bool]
        data_pipeline_native_cloud_connection: Optional[DefenderForContainersGcpOfferingDataPipelineNativeCloudConnection]
        description: str
        enable_audit_logs_auto_provisioning: Optional[bool]
        enable_defender_agent_auto_provisioning: Optional[bool]
        enable_policy_agent_auto_provisioning: Optional[bool]
        installation_method: Optional[Union[str, InstallationMethod]]
        mdc_containers_agentless_discovery_k8_s: Optional[DefenderForContainersGcpOfferingMdcContainersAgentlessDiscoveryK8S]
        mdc_containers_image_assessment: Optional[DefenderForContainersGcpOfferingMdcContainersImageAssessment]
        native_cloud_connection: Optional[DefenderForContainersGcpOfferingNativeCloudConnection]
        offering_type: Literal[OfferingType.DEFENDER_FOR_CONTAINERS_GCP]
        security_gating_enabled: Optional[bool]
        vm_scanners: Optional[DefenderForContainersGcpOfferingVmScanners]

        @overload
        def __init__(
                self, 
                *, 
                container_anti_malware_enabled: Optional[bool] = ..., 
                data_pipeline_native_cloud_connection: Optional[DefenderForContainersGcpOfferingDataPipelineNativeCloudConnection] = ..., 
                enable_audit_logs_auto_provisioning: Optional[bool] = ..., 
                enable_defender_agent_auto_provisioning: Optional[bool] = ..., 
                enable_policy_agent_auto_provisioning: Optional[bool] = ..., 
                installation_method: Optional[Union[str, InstallationMethod]] = ..., 
                mdc_containers_agentless_discovery_k8_s: Optional[DefenderForContainersGcpOfferingMdcContainersAgentlessDiscoveryK8S] = ..., 
                mdc_containers_image_assessment: Optional[DefenderForContainersGcpOfferingMdcContainersImageAssessment] = ..., 
                native_cloud_connection: Optional[DefenderForContainersGcpOfferingNativeCloudConnection] = ..., 
                security_gating_enabled: Optional[bool] = ..., 
                vm_scanners: Optional[DefenderForContainersGcpOfferingVmScanners] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOfferingDataPipelineNativeCloudConnection(_Model):
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOfferingMdcContainersAgentlessDiscoveryK8S(_Model):
        enabled: Optional[bool]
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOfferingMdcContainersImageAssessment(_Model):
        enabled: Optional[bool]
        security_findings_enabled: Optional[bool]
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                security_findings_enabled: Optional[bool] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOfferingNativeCloudConnection(_Model):
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersGcpOfferingVmScanners(VmScannersGcp):
        configuration: VmScannersBaseConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForContainersJFrogOffering(CloudOffering, discriminator='DefenderForContainersJFrog'):
        description: str
        offering_type: Literal[OfferingType.DEFENDER_FOR_CONTAINERS_J_FROG]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForDatabasesGcpOffering(CloudOffering, discriminator='DefenderForDatabasesGcp'):
        arc_auto_provisioning: Optional[DefenderForDatabasesGcpOfferingArcAutoProvisioning]
        defender_for_databases_arc_auto_provisioning: Optional[DefenderForDatabasesGcpOfferingDefenderForDatabasesArcAutoProvisioning]
        description: str
        offering_type: Literal[OfferingType.DEFENDER_FOR_DATABASES_GCP]

        @overload
        def __init__(
                self, 
                *, 
                arc_auto_provisioning: Optional[DefenderForDatabasesGcpOfferingArcAutoProvisioning] = ..., 
                defender_for_databases_arc_auto_provisioning: Optional[DefenderForDatabasesGcpOfferingDefenderForDatabasesArcAutoProvisioning] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForDatabasesGcpOfferingArcAutoProvisioning(ArcAutoProvisioningGcp):
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForDatabasesGcpOfferingDefenderForDatabasesArcAutoProvisioning(_Model):
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersAwsOffering(CloudOffering, discriminator='DefenderForServersAws'):
        arc_auto_provisioning: Optional[DefenderForServersAwsOfferingArcAutoProvisioning]
        defender_for_servers: Optional[DefenderForServersAwsOfferingDefenderForServers]
        description: str
        mde_auto_provisioning: Optional[DefenderForServersAwsOfferingMdeAutoProvisioning]
        offering_type: Literal[OfferingType.DEFENDER_FOR_SERVERS_AWS]
        sub_plan: Optional[DefenderForServersAwsOfferingSubPlan]
        va_auto_provisioning: Optional[DefenderForServersAwsOfferingVaAutoProvisioning]
        vm_scanners: Optional[DefenderForServersAwsOfferingVmScanners]

        @overload
        def __init__(
                self, 
                *, 
                arc_auto_provisioning: Optional[DefenderForServersAwsOfferingArcAutoProvisioning] = ..., 
                defender_for_servers: Optional[DefenderForServersAwsOfferingDefenderForServers] = ..., 
                mde_auto_provisioning: Optional[DefenderForServersAwsOfferingMdeAutoProvisioning] = ..., 
                sub_plan: Optional[DefenderForServersAwsOfferingSubPlan] = ..., 
                va_auto_provisioning: Optional[DefenderForServersAwsOfferingVaAutoProvisioning] = ..., 
                vm_scanners: Optional[DefenderForServersAwsOfferingVmScanners] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingArcAutoProvisioning(ArcAutoProvisioningAws):
        cloud_role_arn: str
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingDefenderForServers(_Model):
        cloud_role_arn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingMdeAutoProvisioning(_Model):
        configuration: Optional[Any]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[Any] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingSubPlan(_Model):
        type: Optional[Union[str, SubPlan]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, SubPlan]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingVaAutoProvisioning(_Model):
        configuration: Optional[DefenderForServersAwsOfferingVaAutoProvisioningConfiguration]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[DefenderForServersAwsOfferingVaAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingVaAutoProvisioningConfiguration(_Model):
        type: Optional[Union[str, Type]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, Type]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersAwsOfferingVmScanners(VmScannersAws):
        cloud_role_arn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersGcpOffering(CloudOffering, discriminator='DefenderForServersGcp'):
        arc_auto_provisioning: Optional[DefenderForServersGcpOfferingArcAutoProvisioning]
        defender_for_servers: Optional[DefenderForServersGcpOfferingDefenderForServers]
        description: str
        mde_auto_provisioning: Optional[DefenderForServersGcpOfferingMdeAutoProvisioning]
        offering_type: Literal[OfferingType.DEFENDER_FOR_SERVERS_GCP]
        sub_plan: Optional[DefenderForServersGcpOfferingSubPlan]
        va_auto_provisioning: Optional[DefenderForServersGcpOfferingVaAutoProvisioning]
        vm_scanners: Optional[DefenderForServersGcpOfferingVmScanners]

        @overload
        def __init__(
                self, 
                *, 
                arc_auto_provisioning: Optional[DefenderForServersGcpOfferingArcAutoProvisioning] = ..., 
                defender_for_servers: Optional[DefenderForServersGcpOfferingDefenderForServers] = ..., 
                mde_auto_provisioning: Optional[DefenderForServersGcpOfferingMdeAutoProvisioning] = ..., 
                sub_plan: Optional[DefenderForServersGcpOfferingSubPlan] = ..., 
                va_auto_provisioning: Optional[DefenderForServersGcpOfferingVaAutoProvisioning] = ..., 
                vm_scanners: Optional[DefenderForServersGcpOfferingVmScanners] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingArcAutoProvisioning(ArcAutoProvisioningGcp):
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[ArcAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingDefenderForServers(_Model):
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingMdeAutoProvisioning(_Model):
        configuration: Optional[Any]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[Any] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingSubPlan(_Model):
        type: Optional[Union[str, SubPlan]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, SubPlan]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingVaAutoProvisioning(_Model):
        configuration: Optional[DefenderForServersGcpOfferingVaAutoProvisioningConfiguration]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[DefenderForServersGcpOfferingVaAutoProvisioningConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingVaAutoProvisioningConfiguration(_Model):
        type: Optional[Union[str, Type]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, Type]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForServersGcpOfferingVmScanners(VmScannersGcp):
        configuration: VmScannersBaseConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForStorageSetting(ExtensionResource):
        id: str
        name: str
        properties: Optional[DefenderForStorageSettingProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DefenderForStorageSettingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DefenderForStorageSettingProperties(_Model):
        is_enabled: Optional[bool]
        malware_scanning: Optional[MalwareScanningProperties]
        managed_by: Optional[Union[str, ManagedByType]]
        override_subscription_level_settings: Optional[bool]
        sensitive_data_discovery: Optional[SensitiveDataDiscoveryProperties]

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ..., 
                malware_scanning: Optional[MalwareScanningProperties] = ..., 
                override_subscription_level_settings: Optional[bool] = ..., 
                sensitive_data_discovery: Optional[SensitiveDataDiscoveryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DenylistCustomAlertRule(ListCustomAlertRule, discriminator='DenylistCustomAlertRule'):
        denylist_values: list[str]
        description: str
        display_name: str
        is_enabled: bool
        rule_type: Literal["DenylistCustomAlertRule"]
        value_type: Union[str, ValueType]

        @overload
        def __init__(
                self, 
                *, 
                denylist_values: list[str], 
                is_enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DevOpsCapability(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.security.models.DevOpsConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[DevOpsConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DevOpsConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DevOpsConfigurationProperties(_Model):
        agentless_configuration: Optional[AgentlessConfiguration]
        authorization: Optional[Authorization]
        auto_discovery: Optional[Union[str, AutoDiscovery]]
        capabilities: Optional[list[DevOpsCapability]]
        provisioning_state: Optional[Union[str, DevOpsProvisioningState]]
        provisioning_status_message: Optional[str]
        provisioning_status_update_time_utc: Optional[datetime]
        top_level_inventory_list: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                agentless_configuration: Optional[AgentlessConfiguration] = ..., 
                authorization: Optional[Authorization] = ..., 
                auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                top_level_inventory_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DevOpsProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETION_FAILURE = "DeletionFailure"
        DELETION_SUCCESS = "DeletionSuccess"
        FAILED = "Failed"
        PENDING = "Pending"
        PENDING_DELETION = "PendingDeletion"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.security.models.DeviceSecurityGroup(ExtensionResource):
        id: str
        name: str
        properties: Optional[DeviceSecurityGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeviceSecurityGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.DeviceSecurityGroupProperties(_Model):
        allowlist_rules: Optional[list[AllowlistCustomAlertRule]]
        denylist_rules: Optional[list[DenylistCustomAlertRule]]
        threshold_rules: Optional[list[ThresholdCustomAlertRule]]
        time_window_rules: Optional[list[TimeWindowCustomAlertRule]]

        @overload
        def __init__(
                self, 
                *, 
                allowlist_rules: Optional[list[AllowlistCustomAlertRule]] = ..., 
                denylist_rules: Optional[list[DenylistCustomAlertRule]] = ..., 
                threshold_rules: Optional[list[ThresholdCustomAlertRule]] = ..., 
                time_window_rules: Optional[list[TimeWindowCustomAlertRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DiscoveredSecuritySolution(ProxyResource):
        id: str
        location: str
        name: str
        properties: DiscoveredSecuritySolutionProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: DiscoveredSecuritySolutionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.DiscoveredSecuritySolutionProperties(_Model):
        offer: str
        publisher: str
        security_family: Union[str, SecurityFamily]
        sku: str

        @overload
        def __init__(
                self, 
                *, 
                offer: str, 
                publisher: str, 
                security_family: Union[str, SecurityFamily], 
                sku: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.DockerHubEnvironmentData(EnvironmentData, discriminator='DockerHubOrganization'):
        authentication: Optional[Authentication]
        environment_type: Literal[EnvironmentType.DOCKER_HUB_ORGANIZATION]
        scan_interval: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[Authentication] = ..., 
                scan_interval: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.Effect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTEST = "Attest"
        AUDIT = "Audit"
        EXEMPT = "Exempt"


    class azure.mgmt.security.models.Enforce(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.security.models.EnvironmentData(_Model):
        environment_type: str

        @overload
        def __init__(
                self, 
                *, 
                environment_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.EnvironmentDetails(_Model):
        environment_hierarchy_id: Optional[str]
        native_resource_id: Optional[str]
        organizational_hierarchy_id: Optional[str]
        subscription_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                environment_hierarchy_id: Optional[str] = ..., 
                native_resource_id: Optional[str] = ..., 
                organizational_hierarchy_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.EnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS_ACCOUNT = "AwsAccount"
        AZURE_DEV_OPS_SCOPE = "AzureDevOpsScope"
        DOCKER_HUB_ORGANIZATION = "DockerHubOrganization"
        GCP_PROJECT = "GcpProject"
        GITHUB_SCOPE = "GithubScope"
        GITLAB_SCOPE = "GitlabScope"
        J_FROG_ARTIFACTORY = "JFrogArtifactory"


    class azure.mgmt.security.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.security.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.security.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.security.models.ExecuteGovernanceRuleParams(_Model):
        override: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                override: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.security.models.Extension(_Model):
        additional_extension_properties: Optional[dict[str, Any]]
        is_enabled: Union[str, IsEnabled]
        name: str
        operation_status: Optional[OperationStatus]
        security_operator_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_extension_properties: Optional[dict[str, Any]] = ..., 
                is_enabled: Union[str, IsEnabled], 
                name: str, 
                security_operator_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.security.models.ExternalSecuritySolution(ProxyResource):
        id: str
        kind: str
        location: Optional[str]
        name: str
        properties: Optional[Any]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ExternalSecuritySolutionKindEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "AAD"
        ATA = "ATA"
        CEF = "CEF"


    class azure.mgmt.security.models.ExternalSecuritySolutionProperties(_Model):
        device_type: Optional[str]
        device_vendor: Optional[str]
        workspace: Optional[ConnectedWorkspace]

        @overload
        def __init__(
                self, 
                *, 
                device_type: Optional[str] = ..., 
                device_vendor: Optional[str] = ..., 
                workspace: Optional[ConnectedWorkspace] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.FileScanFilter(_Model):
        file: Optional[MatchFilter]
        share: Optional[MatchFilter]

        @overload
        def __init__(
                self, 
                *, 
                file: Optional[MatchFilter] = ..., 
                share: Optional[MatchFilter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.FilesScanSummary(_Model):
        failed_files_count: Optional[int]
        malicious_files_count: Optional[int]
        scanned_files_in_gb: Optional[float]
        skipped_files_count: Optional[int]
        total_files_scanned: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                failed_files_count: Optional[int] = ..., 
                malicious_files_count: Optional[int] = ..., 
                scanned_files_in_gb: Optional[float] = ..., 
                skipped_files_count: Optional[int] = ..., 
                total_files_scanned: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GcpAuditLogConfiguration(_Model):
        provisioning_type: Optional[Union[str, GcpLoggingProvisioningType]]
        resource_name_prefix: Optional[str]
        resource_sets: Optional[list[GcpLoggingResourceSet]]

        @overload
        def __init__(
                self, 
                *, 
                provisioning_type: Optional[Union[str, GcpLoggingProvisioningType]] = ..., 
                resource_name_prefix: Optional[str] = ..., 
                resource_sets: Optional[list[GcpLoggingResourceSet]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GcpLoggingProvisioningType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_PROVISIONING = "AutoProvisioning"
        BRING_YOUR_OWN = "BringYourOwn"
        MANUAL_PROVISIONING = "ManualProvisioning"


    class azure.mgmt.security.models.GcpLoggingResourceSet(_Model):
        pub_sub_subscription_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                pub_sub_subscription_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GcpOrganizationalData(_Model):
        organization_membership_type: str

        @overload
        def __init__(
                self, 
                *, 
                organization_membership_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GcpOrganizationalDataMember(GcpOrganizationalData, discriminator='Member'):
        management_project_number: Optional[str]
        organization_membership_type: Literal[OrganizationMembershipType.MEMBER]
        parent_hierarchy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                management_project_number: Optional[str] = ..., 
                parent_hierarchy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GcpOrganizationalDataOrganization(GcpOrganizationalData, discriminator='Organization'):
        excluded_project_numbers: Optional[list[str]]
        organization_membership_type: Literal[OrganizationMembershipType.ORGANIZATION]
        organization_name: Optional[str]
        service_account_email_address: Optional[str]
        workload_identity_provider_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                excluded_project_numbers: Optional[list[str]] = ..., 
                service_account_email_address: Optional[str] = ..., 
                workload_identity_provider_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GcpProjectDetails(_Model):
        project_id: Optional[str]
        project_name: Optional[str]
        project_number: Optional[str]
        workload_identity_pool_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                project_id: Optional[str] = ..., 
                project_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GcpProjectEnvironmentData(EnvironmentData, discriminator='GcpProject'):
        environment_type: Literal[EnvironmentType.GCP_PROJECT]
        organizational_data: Optional[GcpOrganizationalData]
        project_details: Optional[GcpProjectDetails]
        scan_interval: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                organizational_data: Optional[GcpOrganizationalData] = ..., 
                project_details: Optional[GcpProjectDetails] = ..., 
                scan_interval: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GetSensitivitySettingsListResponse(_Model):
        value: Optional[list[GetSensitivitySettingsResponse]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[GetSensitivitySettingsResponse]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GetSensitivitySettingsResponse(ProxyResource):
        id: str
        name: str
        properties: Optional[GetSensitivitySettingsResponseProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GetSensitivitySettingsResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GetSensitivitySettingsResponseProperties(_Model):
        mip_information: Optional[GetSensitivitySettingsResponsePropertiesMipInformation]
        sensitive_info_types_ids: Optional[list[str]]
        sensitivity_threshold_label_id: Optional[str]
        sensitivity_threshold_label_order: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                mip_information: Optional[GetSensitivitySettingsResponsePropertiesMipInformation] = ..., 
                sensitive_info_types_ids: Optional[list[str]] = ..., 
                sensitivity_threshold_label_id: Optional[str] = ..., 
                sensitivity_threshold_label_order: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GetSensitivitySettingsResponsePropertiesMipInformation(_Model):
        built_in_info_types: Optional[list[BuiltInInfoType]]
        custom_info_types: Optional[list[InfoType]]
        labels: Optional[list[Label]]
        mip_integration_status: Optional[Union[str, MipIntegrationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                built_in_info_types: Optional[list[BuiltInInfoType]] = ..., 
                custom_info_types: Optional[list[InfoType]] = ..., 
                labels: Optional[list[Label]] = ..., 
                mip_integration_status: Optional[Union[str, MipIntegrationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitHubOwner(ProxyResource):
        id: str
        name: str
        properties: Optional[GitHubOwnerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GitHubOwnerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitHubOwnerListResponse(_Model):
        next_link: Optional[str]
        value: Optional[list[GitHubOwner]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[GitHubOwner]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitHubOwnerProperties(_Model):
        git_hub_internal_id: Optional[str]
        onboarding_state: Optional[Union[str, OnboardingState]]
        owner_url: Optional[str]
        provisioning_state: Optional[Union[str, DevOpsProvisioningState]]
        provisioning_status_message: Optional[str]
        provisioning_status_update_time_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                onboarding_state: Optional[Union[str, OnboardingState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitHubRepository(ProxyResource):
        id: str
        name: str
        properties: Optional[GitHubRepositoryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GitHubRepositoryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitHubRepositoryProperties(_Model):
        onboarding_state: Optional[Union[str, OnboardingState]]
        parent_owner_name: Optional[str]
        provisioning_state: Optional[Union[str, DevOpsProvisioningState]]
        provisioning_status_message: Optional[str]
        provisioning_status_update_time_utc: Optional[datetime]
        repo_full_name: Optional[str]
        repo_id: Optional[str]
        repo_name: Optional[str]
        repo_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                onboarding_state: Optional[Union[str, OnboardingState]] = ..., 
                parent_owner_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitLabGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[GitLabGroupProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GitLabGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitLabGroupListResponse(_Model):
        next_link: Optional[str]
        value: Optional[list[GitLabGroup]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[GitLabGroup]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitLabGroupProperties(_Model):
        fully_qualified_friendly_name: Optional[str]
        fully_qualified_name: Optional[str]
        onboarding_state: Optional[Union[str, OnboardingState]]
        provisioning_state: Optional[Union[str, DevOpsProvisioningState]]
        provisioning_status_message: Optional[str]
        provisioning_status_update_time_utc: Optional[datetime]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                onboarding_state: Optional[Union[str, OnboardingState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitLabProject(ProxyResource):
        id: str
        name: str
        properties: Optional[GitLabProjectProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GitLabProjectProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitLabProjectProperties(_Model):
        fully_qualified_friendly_name: Optional[str]
        fully_qualified_name: Optional[str]
        fully_qualified_parent_group_name: Optional[str]
        onboarding_state: Optional[Union[str, OnboardingState]]
        provisioning_state: Optional[Union[str, DevOpsProvisioningState]]
        provisioning_status_message: Optional[str]
        provisioning_status_update_time_utc: Optional[datetime]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                onboarding_state: Optional[Union[str, OnboardingState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GithubScopeEnvironmentData(EnvironmentData, discriminator='GithubScope'):
        environment_type: Literal[EnvironmentType.GITHUB_SCOPE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GitlabScopeEnvironmentData(EnvironmentData, discriminator='GitlabScope'):
        environment_type: Literal[EnvironmentType.GITLAB_SCOPE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GovernanceAssignment(ExtensionResource):
        id: str
        name: str
        properties: Optional[GovernanceAssignmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GovernanceAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.GovernanceAssignmentAdditionalData(_Model):
        ticket_link: Optional[str]
        ticket_number: Optional[int]
        ticket_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ticket_link: Optional[str] = ..., 
                ticket_number: Optional[int] = ..., 
                ticket_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GovernanceAssignmentProperties(_Model):
        additional_data: Optional[GovernanceAssignmentAdditionalData]
        governance_email_notification: Optional[GovernanceEmailNotification]
        is_grace_period: Optional[bool]
        owner: Optional[str]
        remediation_due_date: datetime
        remediation_eta: Optional[RemediationEta]

        @overload
        def __init__(
                self, 
                *, 
                additional_data: Optional[GovernanceAssignmentAdditionalData] = ..., 
                governance_email_notification: Optional[GovernanceEmailNotification] = ..., 
                is_grace_period: Optional[bool] = ..., 
                owner: Optional[str] = ..., 
                remediation_due_date: datetime, 
                remediation_eta: Optional[RemediationEta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GovernanceEmailNotification(_Model):
        disable_manager_email_notification: Optional[bool]
        disable_owner_email_notification: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disable_manager_email_notification: Optional[bool] = ..., 
                disable_owner_email_notification: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GovernanceRule(ExtensionResource):
        id: str
        name: str
        properties: Optional[GovernanceRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GovernanceRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.GovernanceRuleEmailNotification(_Model):
        disable_manager_email_notification: Optional[bool]
        disable_owner_email_notification: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disable_manager_email_notification: Optional[bool] = ..., 
                disable_owner_email_notification: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GovernanceRuleMetadata(_Model):
        created_by: Optional[str]
        created_on: Optional[datetime]
        updated_by: Optional[str]
        updated_on: Optional[datetime]


    class azure.mgmt.security.models.GovernanceRuleOwnerSource(_Model):
        type: Optional[Union[str, GovernanceRuleOwnerSourceType]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, GovernanceRuleOwnerSourceType]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GovernanceRuleOwnerSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BY_TAG = "ByTag"
        MANUALLY = "Manually"


    class azure.mgmt.security.models.GovernanceRuleProperties(_Model):
        condition_sets: list[Any]
        description: Optional[str]
        display_name: str
        excluded_scopes: Optional[list[str]]
        governance_email_notification: Optional[GovernanceRuleEmailNotification]
        include_member_scopes: Optional[bool]
        is_disabled: Optional[bool]
        is_grace_period: Optional[bool]
        metadata: Optional[GovernanceRuleMetadata]
        owner_source: GovernanceRuleOwnerSource
        remediation_timeframe: Optional[str]
        rule_priority: int
        rule_type: Union[str, GovernanceRuleType]
        source_resource_type: Union[str, GovernanceRuleSourceResourceType]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                condition_sets: list[Any], 
                description: Optional[str] = ..., 
                display_name: str, 
                excluded_scopes: Optional[list[str]] = ..., 
                governance_email_notification: Optional[GovernanceRuleEmailNotification] = ..., 
                include_member_scopes: Optional[bool] = ..., 
                is_disabled: Optional[bool] = ..., 
                is_grace_period: Optional[bool] = ..., 
                metadata: Optional[GovernanceRuleMetadata] = ..., 
                owner_source: GovernanceRuleOwnerSource, 
                remediation_timeframe: Optional[str] = ..., 
                rule_priority: int, 
                rule_type: Union[str, GovernanceRuleType], 
                source_resource_type: Union[str, GovernanceRuleSourceResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.GovernanceRuleSourceResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSESSMENTS = "Assessments"


    class azure.mgmt.security.models.GovernanceRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTEGRATED = "Integrated"
        SERVICE_NOW = "ServiceNow"


    class azure.mgmt.security.models.HealthDataClassification(_Model):
        component: Optional[str]
        scenario: Optional[str]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                component: Optional[str] = ..., 
                scenario: Optional[str] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.HealthReport(ExtensionResource):
        id: str
        name: str
        properties: Optional[HealthReportProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HealthReportProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.HealthReportProperties(_Model):
        affected_defenders_plans: Optional[list[str]]
        affected_defenders_sub_plans: Optional[list[str]]
        environment_details: Optional[EnvironmentDetails]
        health_data_classification: Optional[HealthDataClassification]
        issues: Optional[list[Issue]]
        report_additional_data: Optional[dict[str, str]]
        resource_details: Optional[ResourceDetails]
        status: Optional[StatusAutoGenerated]

        @overload
        def __init__(
                self, 
                *, 
                affected_defenders_plans: Optional[list[str]] = ..., 
                affected_defenders_sub_plans: Optional[list[str]] = ..., 
                environment_details: Optional[EnvironmentDetails] = ..., 
                health_data_classification: Optional[HealthDataClassification] = ..., 
                issues: Optional[list[Issue]] = ..., 
                resource_details: Optional[ResourceDetails] = ..., 
                status: Optional[StatusAutoGenerated] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ImplementationEffort(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MODERATE = "Moderate"


    class azure.mgmt.security.models.InfoType(_Model):
        description: Optional[str]
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.InformationProtectionKeyword(_Model):
        can_be_numeric: Optional[bool]
        custom: Optional[bool]
        excluded: Optional[bool]
        pattern: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                can_be_numeric: Optional[bool] = ..., 
                custom: Optional[bool] = ..., 
                excluded: Optional[bool] = ..., 
                pattern: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.InformationProtectionPolicy(ExtensionResource):
        id: str
        name: str
        properties: Optional[InformationProtectionPolicyProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[InformationProtectionPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.InformationProtectionPolicyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "custom"
        EFFECTIVE = "effective"


    class azure.mgmt.security.models.InformationProtectionPolicyProperties(_Model):
        information_types: Optional[dict[str, InformationType]]
        labels: Optional[dict[str, SensitivityLabel]]
        last_modified_utc: Optional[datetime]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                information_types: Optional[dict[str, InformationType]] = ..., 
                labels: Optional[dict[str, SensitivityLabel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.InformationType(_Model):
        custom: Optional[bool]
        description: Optional[str]
        display_name: Optional[str]
        enabled: Optional[bool]
        keywords: Optional[list[InformationProtectionKeyword]]
        order: Optional[int]
        recommended_label_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                keywords: Optional[list[InformationProtectionKeyword]] = ..., 
                order: Optional[int] = ..., 
                recommended_label_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.InheritFromParentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.Inherited(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.security.models.InstallationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARC = "Arc"
        HELM = "Helm"


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


    class azure.mgmt.security.models.InventoryList(_Model):
        inventory_kind: Optional[Union[str, InventoryKind]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                inventory_kind: Optional[Union[str, InventoryKind]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.InventoryListKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUSION = "Exclusion"
        INCLUSION = "Inclusion"


    class azure.mgmt.security.models.IoTSecurityAggregatedAlert(ProxyResource):
        id: str
        name: str
        properties: Optional[IoTSecurityAggregatedAlertProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IoTSecurityAggregatedAlertProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.IoTSecurityAggregatedAlertProperties(_Model):
        action_taken: Optional[str]
        aggregated_date_utc: Optional[date]
        alert_display_name: Optional[str]
        alert_type: Optional[str]
        count: Optional[int]
        description: Optional[str]
        effected_resource_type: Optional[str]
        log_analytics_query: Optional[str]
        remediation_steps: Optional[str]
        reported_severity: Optional[Union[str, ReportedSeverity]]
        system_source: Optional[str]
        top_devices_list: Optional[list[IoTSecurityAggregatedAlertPropertiesTopDevicesListItem]]
        vendor_name: Optional[str]


    class azure.mgmt.security.models.IoTSecurityAggregatedAlertPropertiesTopDevicesListItem(_Model):
        alerts_count: Optional[int]
        device_id: Optional[str]
        last_occurrence: Optional[str]


    class azure.mgmt.security.models.IoTSecurityAggregatedRecommendation(ProxyResource):
        id: str
        name: str
        properties: Optional[IoTSecurityAggregatedRecommendationProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IoTSecurityAggregatedRecommendationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.IoTSecurityAggregatedRecommendationProperties(_Model):
        description: Optional[str]
        detected_by: Optional[str]
        healthy_devices: Optional[int]
        log_analytics_query: Optional[str]
        recommendation_display_name: Optional[str]
        recommendation_name: Optional[str]
        recommendation_type_id: Optional[str]
        remediation_steps: Optional[str]
        reported_severity: Optional[Union[str, ReportedSeverity]]
        unhealthy_device_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                recommendation_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.IoTSecurityAlertedDevice(_Model):
        alerts_count: Optional[int]
        device_id: Optional[str]


    class azure.mgmt.security.models.IoTSecurityDeviceAlert(_Model):
        alert_display_name: Optional[str]
        alerts_count: Optional[int]
        reported_severity: Optional[Union[str, ReportedSeverity]]


    class azure.mgmt.security.models.IoTSecurityDeviceRecommendation(_Model):
        devices_count: Optional[int]
        recommendation_display_name: Optional[str]
        reported_severity: Optional[Union[str, ReportedSeverity]]


    class azure.mgmt.security.models.IoTSecuritySolutionAnalyticsModel(ProxyResource):
        id: str
        name: str
        properties: Optional[IoTSecuritySolutionAnalyticsModelProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IoTSecuritySolutionAnalyticsModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.IoTSecuritySolutionAnalyticsModelList(_Model):
        next_link: Optional[str]
        value: list[IoTSecuritySolutionAnalyticsModel]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[IoTSecuritySolutionAnalyticsModel]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.IoTSecuritySolutionAnalyticsModelProperties(_Model):
        devices_metrics: Optional[list[IoTSecuritySolutionAnalyticsModelPropertiesDevicesMetricsItem]]
        metrics: Optional[IoTSeverityMetrics]
        most_prevalent_device_alerts: Optional[list[IoTSecurityDeviceAlert]]
        most_prevalent_device_recommendations: Optional[list[IoTSecurityDeviceRecommendation]]
        top_alerted_devices: Optional[list[IoTSecurityAlertedDevice]]
        unhealthy_device_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                most_prevalent_device_alerts: Optional[list[IoTSecurityDeviceAlert]] = ..., 
                most_prevalent_device_recommendations: Optional[list[IoTSecurityDeviceRecommendation]] = ..., 
                top_alerted_devices: Optional[list[IoTSecurityAlertedDevice]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.IoTSecuritySolutionAnalyticsModelPropertiesDevicesMetricsItem(_Model):
        date: Optional[datetime]
        devices_metrics: Optional[IoTSeverityMetrics]

        @overload
        def __init__(
                self, 
                *, 
                date: Optional[datetime] = ..., 
                devices_metrics: Optional[IoTSeverityMetrics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.IoTSecuritySolutionModel(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[IoTSecuritySolutionProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[IoTSecuritySolutionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.IoTSecuritySolutionProperties(_Model):
        additional_workspaces: Optional[list[AdditionalWorkspacesProperties]]
        auto_discovered_resources: Optional[list[str]]
        disabled_data_sources: Optional[list[Union[str, DataSource]]]
        display_name: str
        export: Optional[list[Union[str, ExportData]]]
        iot_hubs: list[str]
        recommendations_configuration: Optional[list[RecommendationConfigurationProperties]]
        status: Optional[Union[str, SecuritySolutionStatus]]
        unmasked_ip_logging_status: Optional[Union[str, UnmaskedIpLoggingStatus]]
        user_defined_resources: Optional[UserDefinedResourcesProperties]
        workspace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_workspaces: Optional[list[AdditionalWorkspacesProperties]] = ..., 
                disabled_data_sources: Optional[list[Union[str, DataSource]]] = ..., 
                display_name: str, 
                export: Optional[list[Union[str, ExportData]]] = ..., 
                iot_hubs: list[str], 
                recommendations_configuration: Optional[list[RecommendationConfigurationProperties]] = ..., 
                status: Optional[Union[str, SecuritySolutionStatus]] = ..., 
                unmasked_ip_logging_status: Optional[Union[str, UnmaskedIpLoggingStatus]] = ..., 
                user_defined_resources: Optional[UserDefinedResourcesProperties] = ..., 
                workspace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.IoTSeverityMetrics(_Model):
        high: Optional[int]
        low: Optional[int]
        medium: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                high: Optional[int] = ..., 
                low: Optional[int] = ..., 
                medium: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.IsEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.security.models.Issue(_Model):
        issue_additional_data: Optional[dict[str, str]]
        issue_description: Optional[str]
        issue_key: str
        issue_name: Optional[str]
        remediation_script: Optional[str]
        remediation_steps: Optional[str]
        security_values: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                issue_additional_data: Optional[dict[str, str]] = ..., 
                issue_description: Optional[str] = ..., 
                issue_key: str, 
                issue_name: Optional[str] = ..., 
                remediation_script: Optional[str] = ..., 
                remediation_steps: Optional[str] = ..., 
                security_values: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.IssueCreationRequest(_Model):
        security_assessment_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                security_assessment_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.JFrogEnvironmentData(EnvironmentData, discriminator='JFrogArtifactory'):
        environment_type: Literal[EnvironmentType.J_FROG_ARTIFACTORY]
        scan_interval: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                scan_interval: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicy(ProxyResource):
        id: str
        kind: Optional[str]
        location: str
        name: str
        properties: JitNetworkAccessPolicyProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: JitNetworkAccessPolicyProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicyInitiatePort(_Model):
        allowed_source_address_prefix: Optional[str]
        end_time_utc: datetime
        number: int

        @overload
        def __init__(
                self, 
                *, 
                allowed_source_address_prefix: Optional[str] = ..., 
                end_time_utc: datetime, 
                number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicyInitiateRequest(_Model):
        justification: Optional[str]
        virtual_machines: list[JitNetworkAccessPolicyInitiateVirtualMachine]

        @overload
        def __init__(
                self, 
                *, 
                justification: Optional[str] = ..., 
                virtual_machines: list[JitNetworkAccessPolicyInitiateVirtualMachine]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicyInitiateVirtualMachine(_Model):
        id: str
        ports: list[JitNetworkAccessPolicyInitiatePort]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                ports: list[JitNetworkAccessPolicyInitiatePort]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicyProperties(_Model):
        provisioning_state: Optional[str]
        requests: Optional[list[JitNetworkAccessRequest]]
        virtual_machines: list[JitNetworkAccessPolicyVirtualMachine]

        @overload
        def __init__(
                self, 
                *, 
                requests: Optional[list[JitNetworkAccessRequest]] = ..., 
                virtual_machines: list[JitNetworkAccessPolicyVirtualMachine]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.JitNetworkAccessPolicyVirtualMachine(_Model):
        id: str
        ports: list[JitNetworkAccessPortRule]
        public_ip_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                ports: list[JitNetworkAccessPortRule], 
                public_ip_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.JitNetworkAccessPortRule(_Model):
        allowed_source_address_prefix: Optional[str]
        allowed_source_address_prefixes: Optional[list[str]]
        max_request_access_duration: str
        number: int
        protocol: Union[str, ProtocolEnum]

        @overload
        def __init__(
                self, 
                *, 
                allowed_source_address_prefix: Optional[str] = ..., 
                allowed_source_address_prefixes: Optional[list[str]] = ..., 
                max_request_access_duration: str, 
                number: int, 
                protocol: Union[str, ProtocolEnum]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.JitNetworkAccessRequest(_Model):
        justification: Optional[str]
        requestor: str
        start_time_utc: datetime
        virtual_machines: list[JitNetworkAccessRequestVirtualMachine]

        @overload
        def __init__(
                self, 
                *, 
                justification: Optional[str] = ..., 
                requestor: str, 
                start_time_utc: datetime, 
                virtual_machines: list[JitNetworkAccessRequestVirtualMachine]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.JitNetworkAccessRequestPort(_Model):
        allowed_source_address_prefix: Optional[str]
        allowed_source_address_prefixes: Optional[list[str]]
        end_time_utc: datetime
        mapped_port: Optional[int]
        number: int
        status: Union[str, Status]
        status_reason: Union[str, StatusReason]

        @overload
        def __init__(
                self, 
                *, 
                allowed_source_address_prefix: Optional[str] = ..., 
                allowed_source_address_prefixes: Optional[list[str]] = ..., 
                end_time_utc: datetime, 
                mapped_port: Optional[int] = ..., 
                number: int, 
                status: Union[str, Status], 
                status_reason: Union[str, StatusReason]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.JitNetworkAccessRequestVirtualMachine(_Model):
        id: str
        ports: list[JitNetworkAccessRequestPort]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                ports: list[JitNetworkAccessRequestPort]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.KindEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUNDLES = "Bundles"


    class azure.mgmt.security.models.Label(_Model):
        id: Optional[str]
        name: Optional[str]
        order: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                order: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ListCustomAlertRule(CustomAlertRule, discriminator='ListCustomAlertRule'):
        description: str
        display_name: str
        is_enabled: bool
        rule_type: Literal["ListCustomAlertRule"]
        value_type: Optional[Union[str, ValueType]]

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.LogAnalyticsIdentifier(ResourceIdentifier, discriminator='LogAnalytics'):
        agent_id: Optional[str]
        type: Literal[ResourceIdentifierType.LOG_ANALYTICS]
        workspace_id: Optional[str]
        workspace_resource_group: Optional[str]
        workspace_subscription_id: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.MalwareScan(ExtensionResource):
        id: str
        name: str
        properties: Optional[MalwareScanProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MalwareScanProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.MalwareScanFilters(_Model):
        blobs: Optional[BlobScanFilter]
        files: Optional[FileScanFilter]

        @overload
        def __init__(
                self, 
                *, 
                blobs: Optional[BlobScanFilter] = ..., 
                files: Optional[FileScanFilter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.MalwareScanProperties(_Model):
        scan_end_time: Optional[datetime]
        scan_id: Optional[str]
        scan_start_time: Optional[datetime]
        scan_status: Optional[Union[str, MalwareScanStatus]]
        scan_status_message: Optional[str]
        scan_summary: Optional[ScanSummary]

        @overload
        def __init__(
                self, 
                *, 
                scan_end_time: Optional[datetime] = ..., 
                scan_id: Optional[str] = ..., 
                scan_start_time: Optional[datetime] = ..., 
                scan_status: Optional[Union[str, MalwareScanStatus]] = ..., 
                scan_status_message: Optional[str] = ..., 
                scan_summary: Optional[ScanSummary] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.MalwareScanStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELING = "Canceling"
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        QUEUED = "Queued"
        WAITING_FOR_COMPLETION = "WaitingForCompletion"


    class azure.mgmt.security.models.MalwareScanningProperties(_Model):
        automated_response: Optional[Union[str, AutomatedResponseType]]
        blob_scan_results_options: Optional[Union[str, BlobScanResultsOptions]]
        on_upload: Optional[OnUploadProperties]
        operation_status: Optional[OperationStatus]
        scan_results_event_grid_topic_resource_id: Optional[str]
        scanner_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                automated_response: Optional[Union[str, AutomatedResponseType]] = ..., 
                blob_scan_results_options: Optional[Union[str, BlobScanResultsOptions]] = ..., 
                on_upload: Optional[OnUploadProperties] = ..., 
                scan_results_event_grid_topic_resource_id: Optional[str] = ..., 
                scanner_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ManagedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_DEFENDER_XDR = "MicrosoftDefenderXDR"
        NONE = "None"
        SUBSCRIPTION_SETTINGS_ENFORCER = "SubscriptionSettingsEnforcer"


    class azure.mgmt.security.models.MatchFilter(_Model):
        match: Union[str, MatchType]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                match: Union[str, MatchType], 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.MatchType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXACT = "Exact"
        PREFIX = "Prefix"


    class azure.mgmt.security.models.MdeOnboardingData(ProxyResource):
        id: str
        name: str
        properties: Optional[MdeOnboardingDataProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MdeOnboardingDataProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.MdeOnboardingDataList(_Model):
        value: Optional[list[MdeOnboardingData]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[MdeOnboardingData]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.MdeOnboardingDataProperties(_Model):
        onboarding_package_linux: Optional[bytes]
        onboarding_package_windows: Optional[bytes]

        @overload
        def __init__(
                self, 
                *, 
                onboarding_package_linux: Optional[bytes] = ..., 
                onboarding_package_windows: Optional[bytes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.security.models.NotificationsSource(_Model):
        source_type: str

        @overload
        def __init__(
                self, 
                *, 
                source_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.NotificationsSourceAlert(NotificationsSource, discriminator='Alert'):
        minimal_severity: Optional[Union[str, MinimalSeverity]]
        source_type: Literal[SourceType.ALERT]

        @overload
        def __init__(
                self, 
                *, 
                minimal_severity: Optional[Union[str, MinimalSeverity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.NotificationsSourceAttackPath(NotificationsSource, discriminator='AttackPath'):
        minimal_risk_level: Optional[Union[str, MinimalRiskLevel]]
        source_type: Literal[SourceType.ATTACK_PATH]

        @overload
        def __init__(
                self, 
                *, 
                minimal_risk_level: Optional[Union[str, MinimalRiskLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.security.models.OnPremiseResourceDetails(CommonResourceDetails, discriminator='OnPremiseResourceDetails'):
        machine_name: str
        source: Literal[Source.ON_PREMISE_RESOURCE_DETAILS]
        source_computer_id: str
        vmuuid: str
        workspace_id: str

        @overload
        def __init__(
                self, 
                *, 
                machine_name: str, 
                source_computer_id: str, 
                vmuuid: str, 
                workspace_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.OnPremiseSqlResourceDetails(OnPremiseResourceDetails, discriminator='OnPremiseSql'):
        database_name: str
        machine_name: str
        server_name: str
        source: Literal[Source.ON_PREMISE_SQL]
        source_computer_id: str
        vmuuid: str
        workspace_id: str

        @overload
        def __init__(
                self, 
                *, 
                database_name: str, 
                machine_name: str, 
                server_name: str, 
                source_computer_id: str, 
                vmuuid: str, 
                workspace_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.OnUploadFilters(_Model):
        exclude_blobs_larger_than: Optional[int]
        exclude_blobs_with_prefix: Optional[list[str]]
        exclude_blobs_with_suffix: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                exclude_blobs_larger_than: Optional[int] = ..., 
                exclude_blobs_with_prefix: Optional[list[str]] = ..., 
                exclude_blobs_with_suffix: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.OnUploadProperties(_Model):
        cap_gb_per_month: Optional[int]
        filters: Optional[OnUploadFilters]
        is_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cap_gb_per_month: Optional[int] = ..., 
                filters: Optional[OnUploadFilters] = ..., 
                is_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.OnboardingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_APPLICABLE = "NotApplicable"
        NOT_ONBOARDED = "NotOnboarded"
        ONBOARDED = "Onboarded"
        ONBOARDED_BY_OTHER_CONNECTOR = "OnboardedByOtherConnector"


    class azure.mgmt.security.models.Operation(_Model):
        action_type: Optional[Union[str, ArmActionType]]
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


    class azure.mgmt.security.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.security.models.OperationResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.security.models.OperationResultAutoGenerated(_Model):
        status: Optional[Union[str, OperationResult]]


    class azure.mgmt.security.models.OperationStatus(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.security.models.OriginatedFrom(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        M365 = "M365"


    class azure.mgmt.security.models.PartialAssessmentProperties(_Model):
        assessment_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assessment_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.Pricing(ExtensionResource):
        id: str
        name: str
        properties: Optional[PricingProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PricingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.PricingBatch(ExtensionResource):
        id: str
        name: str
        properties: Optional[PricingBatchProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PricingBatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.PricingBatchPlanItem(_Model):
        operation_status: Optional[PricingPlanOperationStatus]
        plan_name: str
        properties: PricingPropertiesReference

        @overload
        def __init__(
                self, 
                *, 
                plan_name: str, 
                properties: PricingPropertiesReference
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.PricingBatchProperties(_Model):
        plans_configurations: list[PricingBatchPlanItem]

        @overload
        def __init__(
                self, 
                *, 
                plans_configurations: list[PricingBatchPlanItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.PricingList(_Model):
        value: list[Pricing]

        @overload
        def __init__(
                self, 
                *, 
                value: list[Pricing]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.PricingPlanOperationStatus(_Model):
        code: Optional[Union[str, PricingPlanOperationStatusCode]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, PricingPlanOperationStatusCode]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.PricingPlanOperationStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.security.models.PricingProperties(_Model):
        deprecated: Optional[bool]
        enablement_time: Optional[datetime]
        enforce: Optional[Union[str, Enforce]]
        extensions: Optional[list[Extension]]
        free_trial_remaining_time: Optional[timedelta]
        inherited: Optional[Union[str, Inherited]]
        inherited_from: Optional[str]
        managed_by: Optional[str]
        originated_from: Optional[Union[str, OriginatedFrom]]
        pricing_tier: Union[str, PricingTier]
        replaced_by: Optional[list[str]]
        resources_coverage_status: Optional[Union[str, ResourcesCoverageStatus]]
        security_operator_resource_id: Optional[str]
        sub_plan: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enforce: Optional[Union[str, Enforce]] = ..., 
                extensions: Optional[list[Extension]] = ..., 
                pricing_tier: Union[str, PricingTier], 
                security_operator_resource_id: Optional[str] = ..., 
                sub_plan: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.PricingPropertiesReference(_Model):


    class azure.mgmt.security.models.PricingTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE = "Free"
        STANDARD = "Standard"


    class azure.mgmt.security.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.security.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.security.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.security.models.PrivateLinkGroupResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.PrivateLinkProperties(_Model):
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        private_link_resources: Optional[list[PrivateLinkGroupResource]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.PrivateLinkResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: PrivateLinkProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: PrivateLinkProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.PrivateLinkUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.security.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.security.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.QueryCheck(_Model):
        column_names: Optional[list[str]]
        expected_result: Optional[list[list[str]]]
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                column_names: Optional[list[str]] = ..., 
                expected_result: Optional[list[list[str]]] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.Rank(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        NONE = "None"


    class azure.mgmt.security.models.RecommendationConfigStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.RecommendationConfigurationProperties(_Model):
        name: Optional[str]
        recommendation_type: Union[str, RecommendationType]
        status: Union[str, RecommendationConfigStatus]

        @overload
        def __init__(
                self, 
                *, 
                recommendation_type: Union[str, RecommendationType], 
                status: Union[str, RecommendationConfigStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.security.models.RegulatoryComplianceAssessment(ProxyResource):
        id: str
        name: str
        properties: Optional[RegulatoryComplianceAssessmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RegulatoryComplianceAssessmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.RegulatoryComplianceAssessmentProperties(_Model):
        assessment_details_link: Optional[str]
        assessment_type: Optional[str]
        description: Optional[str]
        failed_resources: Optional[int]
        passed_resources: Optional[int]
        skipped_resources: Optional[int]
        state: Optional[Union[str, State]]
        unsupported_resources: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.RegulatoryComplianceControl(ProxyResource):
        id: str
        name: str
        properties: Optional[RegulatoryComplianceControlProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RegulatoryComplianceControlProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.RegulatoryComplianceControlProperties(_Model):
        description: Optional[str]
        failed_assessments: Optional[int]
        passed_assessments: Optional[int]
        skipped_assessments: Optional[int]
        state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.RegulatoryComplianceStandard(ProxyResource):
        id: str
        name: str
        properties: Optional[RegulatoryComplianceStandardProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RegulatoryComplianceStandardProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.RegulatoryComplianceStandardProperties(_Model):
        failed_controls: Optional[int]
        passed_controls: Optional[int]
        skipped_controls: Optional[int]
        state: Optional[Union[str, State]]
        unsupported_controls: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.Remediation(_Model):
        automated: Optional[bool]
        description: Optional[str]
        portal_link: Optional[str]
        scripts: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                automated: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                portal_link: Optional[str] = ..., 
                scripts: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.RemediationEta(_Model):
        eta: datetime
        justification: str

        @overload
        def __init__(
                self, 
                *, 
                eta: datetime, 
                justification: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ReportedSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        INFORMATIONAL = "Informational"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.security.models.ResourceDetails(_Model):
        connector_id: Optional[str]
        id: Optional[str]
        source: Optional[Union[str, Source]]

        @overload
        def __init__(
                self, 
                *, 
                source: Optional[Union[str, Source]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ResourceIdentifier(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ResourceIdentifierType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_RESOURCE = "AzureResource"
        LOG_ANALYTICS = "LogAnalytics"


    class azure.mgmt.security.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"


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
        CRITICAL = "Critical"
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        NONE = "None"


    class azure.mgmt.security.models.RuleCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARTIFACTS = "Artifacts"
        CODE = "Code"
        CONTAINERS = "Containers"
        DEPENDENCIES = "Dependencies"
        IA_C = "IaC"
        SECRETS = "Secrets"


    class azure.mgmt.security.models.RuleResults(ExtensionResource):
        id: str
        name: str
        properties: Optional[RuleResultsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RuleResultsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.RuleResultsInput(_Model):
        latest_scan: Optional[bool]
        results: Optional[list[list[str]]]

        @overload
        def __init__(
                self, 
                *, 
                latest_scan: Optional[bool] = ..., 
                results: Optional[list[list[str]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.RuleResultsProperties(_Model):
        latest_scan: Optional[bool]
        results: Optional[list[list[str]]]

        @overload
        def __init__(
                self, 
                *, 
                latest_scan: Optional[bool] = ..., 
                results: Optional[list[list[str]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.security.models.RuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASELINE_EXPECTED = "BaselineExpected"
        BINARY = "Binary"
        NEGATIVE_LIST = "NegativeList"
        POSITIVE_LIST = "PositiveList"


    class azure.mgmt.security.models.RulesResults(_Model):
        next_link: Optional[str]
        value: Optional[list[RuleResults]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[RuleResults]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.RulesResultsInput(_Model):
        latest_scan: Optional[bool]
        results: Optional[dict[str, list[list[str]]]]

        @overload
        def __init__(
                self, 
                *, 
                latest_scan: Optional[bool] = ..., 
                results: Optional[dict[str, list[list[str]]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ScanOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        FAILED_TO_RUN = "FailedToRun"
        IN_PROGRESS = "InProgress"
        PASSED = "Passed"


    class azure.mgmt.security.models.ScanPropertiesV2(_Model):
        database: Optional[str]
        end_time: Optional[datetime]
        high_severity_failed_rules_count: Optional[int]
        is_baseline_applied: Optional[bool]
        last_scan_time: Optional[datetime]
        low_severity_failed_rules_count: Optional[int]
        medium_severity_failed_rules_count: Optional[int]
        server: Optional[str]
        sql_version: Optional[str]
        start_time: Optional[datetime]
        state: Optional[Union[str, ScanState]]
        total_failed_rules_count: Optional[int]
        total_passed_rules_count: Optional[int]
        total_rules_count: Optional[int]
        trigger_type: Optional[Union[str, ScanTriggerType]]

        @overload
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
                trigger_type: Optional[Union[str, ScanTriggerType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ScanResult(ExtensionResource):
        id: str
        name: str
        properties: Optional[ScanResultProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScanResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ScanResultProperties(_Model):
        baseline_adjusted_result: Optional[BaselineAdjustedResult]
        is_trimmed: Optional[bool]
        query_results: Optional[list[list[str]]]
        remediation: Optional[Remediation]
        rule_id: Optional[str]
        rule_metadata: Optional[VaRule]
        status: Optional[Union[str, RuleStatus]]

        @overload
        def __init__(
                self, 
                *, 
                baseline_adjusted_result: Optional[BaselineAdjustedResult] = ..., 
                is_trimmed: Optional[bool] = ..., 
                query_results: Optional[list[list[str]]] = ..., 
                remediation: Optional[Remediation] = ..., 
                rule_id: Optional[str] = ..., 
                rule_metadata: Optional[VaRule] = ..., 
                status: Optional[Union[str, RuleStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ScanState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        FAILED_TO_RUN = "FailedToRun"
        IN_PROGRESS = "InProgress"
        PASSED = "Passed"


    class azure.mgmt.security.models.ScanSummary(_Model):
        blobs: Optional[BlobsScanSummary]
        estimated_scan_cost_usd: Optional[float]
        files: Optional[FilesScanSummary]

        @overload
        def __init__(
                self, 
                *, 
                blobs: Optional[BlobsScanSummary] = ..., 
                estimated_scan_cost_usd: Optional[float] = ..., 
                files: Optional[FilesScanSummary] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ScanTriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_DEMAND = "OnDemand"
        RECURRING = "Recurring"


    class azure.mgmt.security.models.ScanV2(ExtensionResource):
        id: str
        name: str
        properties: Optional[ScanPropertiesV2]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScanPropertiesV2] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ScanningMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"


    class azure.mgmt.security.models.ScopeElement(_Model):
        field: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                field: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ScoreDetails(_Model):
        current: Optional[float]
        max: Optional[int]
        percentage: Optional[float]


    class azure.mgmt.security.models.SecureScoreControlDefinitionItem(Resource):
        id: str
        name: str
        properties: Optional[SecureScoreControlDefinitionItemProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecureScoreControlDefinitionItemProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecureScoreControlDefinitionItemProperties(_Model):
        assessment_definitions: Optional[list[AzureResourceLink]]
        description: Optional[str]
        display_name: Optional[str]
        max_score: Optional[int]
        source: Optional[SecureScoreControlDefinitionSource]


    class azure.mgmt.security.models.SecureScoreControlDefinitionSource(_Model):
        source_type: Optional[Union[str, ControlType]]

        @overload
        def __init__(
                self, 
                *, 
                source_type: Optional[Union[str, ControlType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecureScoreControlDetails(Resource):
        id: str
        name: str
        properties: Optional[SecureScoreControlScoreDetails]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecureScoreControlScoreDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecureScoreControlScoreDetails(_Model):
        definition: Optional[SecureScoreControlDefinitionItem]
        display_name: Optional[str]
        healthy_resource_count: Optional[int]
        not_applicable_resource_count: Optional[int]
        score: Optional[ScoreDetails]
        unhealthy_resource_count: Optional[int]
        weight: Optional[int]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                definition: Optional[SecureScoreControlDefinitionItem] = ..., 
                score: Optional[ScoreDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecureScoreItem(ProxyResource):
        id: str
        name: str
        properties: Optional[SecureScoreItemProperties]
        system_data: SystemData
        type: str


    class azure.mgmt.security.models.SecureScoreItemProperties(_Model):
        display_name: Optional[str]
        score: Optional[ScoreDetails]
        weight: Optional[int]


    class azure.mgmt.security.models.SecurityAssessment(Resource):
        id: str
        name: str
        properties: Optional[SecurityAssessmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityAssessmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataPartnerData(_Model):
        partner_name: str
        product_name: Optional[str]
        secret: str

        @overload
        def __init__(
                self, 
                *, 
                partner_name: str, 
                product_name: Optional[str] = ..., 
                secret: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataProperties(_Model):
        assessment_type: Union[str, AssessmentType]
        categories: Optional[list[Union[str, Categories]]]
        description: Optional[str]
        display_name: str
        implementation_effort: Optional[Union[str, ImplementationEffort]]
        partner_data: Optional[SecurityAssessmentMetadataPartnerData]
        policy_definition_id: Optional[str]
        preview: Optional[bool]
        remediation_description: Optional[str]
        severity: Union[str, Severity]
        threats: Optional[list[Union[str, Threats]]]
        user_impact: Optional[Union[str, UserImpact]]

        @overload
        def __init__(
                self, 
                *, 
                assessment_type: Union[str, AssessmentType], 
                categories: Optional[list[Union[str, Categories]]] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                implementation_effort: Optional[Union[str, ImplementationEffort]] = ..., 
                partner_data: Optional[SecurityAssessmentMetadataPartnerData] = ..., 
                preview: Optional[bool] = ..., 
                remediation_description: Optional[str] = ..., 
                severity: Union[str, Severity], 
                threats: Optional[list[Union[str, Threats]]] = ..., 
                user_impact: Optional[Union[str, UserImpact]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataPropertiesResponse(SecurityAssessmentMetadataProperties):
        assessment_type: Union[str, AssessmentType]
        categories: Union[list[str, Categories]]
        description: str
        display_name: str
        implementation_effort: Union[str, ImplementationEffort]
        partner_data: SecurityAssessmentMetadataPartnerData
        planned_deprecation_date: Optional[str]
        policy_definition_id: str
        preview: bool
        publish_dates: Optional[SecurityAssessmentMetadataPropertiesResponsePublishDates]
        remediation_description: str
        severity: Union[str, Severity]
        tactics: Optional[list[Union[str, Tactics]]]
        techniques: Optional[list[Union[str, Techniques]]]
        threats: Union[list[str, Threats]]
        user_impact: Union[str, UserImpact]

        @overload
        def __init__(
                self, 
                *, 
                assessment_type: Union[str, AssessmentType], 
                categories: Optional[list[Union[str, Categories]]] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                implementation_effort: Optional[Union[str, ImplementationEffort]] = ..., 
                partner_data: Optional[SecurityAssessmentMetadataPartnerData] = ..., 
                planned_deprecation_date: Optional[str] = ..., 
                preview: Optional[bool] = ..., 
                publish_dates: Optional[SecurityAssessmentMetadataPropertiesResponsePublishDates] = ..., 
                remediation_description: Optional[str] = ..., 
                severity: Union[str, Severity], 
                tactics: Optional[list[Union[str, Tactics]]] = ..., 
                techniques: Optional[list[Union[str, Techniques]]] = ..., 
                threats: Optional[list[Union[str, Threats]]] = ..., 
                user_impact: Optional[Union[str, UserImpact]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataPropertiesResponsePublishDates(_Model):
        ga: Optional[str]
        public: str

        @overload
        def __init__(
                self, 
                *, 
                ga: Optional[str] = ..., 
                public: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentMetadataResponse(ProxyResource):
        id: str
        name: str
        properties: Optional[SecurityAssessmentMetadataPropertiesResponse]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityAssessmentMetadataPropertiesResponse] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentPartnerData(_Model):
        partner_name: str
        secret: str

        @overload
        def __init__(
                self, 
                *, 
                partner_name: str, 
                secret: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentProperties(SecurityAssessmentPropertiesBase):
        additional_data: dict[str, str]
        display_name: str
        links: AssessmentLinks
        metadata: SecurityAssessmentMetadataProperties
        partners_data: SecurityAssessmentPartnerData
        resource_details: CommonResourceDetails
        risk: SecurityAssessmentPropertiesBaseRisk
        status: AssessmentStatus

        @overload
        def __init__(
                self, 
                *, 
                additional_data: Optional[dict[str, str]] = ..., 
                metadata: Optional[SecurityAssessmentMetadataProperties] = ..., 
                partners_data: Optional[SecurityAssessmentPartnerData] = ..., 
                resource_details: CommonResourceDetails, 
                risk: Optional[SecurityAssessmentPropertiesBaseRisk] = ..., 
                status: AssessmentStatus
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesBase(_Model):
        additional_data: Optional[dict[str, str]]
        display_name: Optional[str]
        links: Optional[AssessmentLinks]
        metadata: Optional[SecurityAssessmentMetadataProperties]
        partners_data: Optional[SecurityAssessmentPartnerData]
        resource_details: CommonResourceDetails
        risk: Optional[SecurityAssessmentPropertiesBaseRisk]

        @overload
        def __init__(
                self, 
                *, 
                additional_data: Optional[dict[str, str]] = ..., 
                metadata: Optional[SecurityAssessmentMetadataProperties] = ..., 
                partners_data: Optional[SecurityAssessmentPartnerData] = ..., 
                resource_details: CommonResourceDetails, 
                risk: Optional[SecurityAssessmentPropertiesBaseRisk] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesBaseRisk(_Model):
        attack_paths_references: Optional[list[str]]
        is_contextual_risk: Optional[bool]
        level: Optional[Union[str, RiskLevel]]
        paths: Optional[list[SecurityAssessmentPropertiesBaseRiskPathsItem]]
        risk_factors: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                attack_paths_references: Optional[list[str]] = ..., 
                is_contextual_risk: Optional[bool] = ..., 
                level: Optional[Union[str, RiskLevel]] = ..., 
                paths: Optional[list[SecurityAssessmentPropertiesBaseRiskPathsItem]] = ..., 
                risk_factors: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesBaseRiskPathsItem(_Model):
        edges: Optional[list[SecurityAssessmentPropertiesBaseRiskPathsItemEdgeItem]]
        id: Optional[str]
        nodes: Optional[list[SecurityAssessmentPropertiesBaseRiskPathsItemNodesItem]]

        @overload
        def __init__(
                self, 
                *, 
                edges: Optional[list[SecurityAssessmentPropertiesBaseRiskPathsItemEdgeItem]] = ..., 
                id: Optional[str] = ..., 
                nodes: Optional[list[SecurityAssessmentPropertiesBaseRiskPathsItemNodesItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesBaseRiskPathsItemEdgeItem(_Model):
        id: str
        source_id: str
        target_id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                source_id: str, 
                target_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesBaseRiskPathsItemNodesItem(_Model):
        id: Optional[str]
        node_properties_label: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                node_properties_label: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentPropertiesResponse(SecurityAssessmentPropertiesBase):
        additional_data: dict[str, str]
        display_name: str
        links: AssessmentLinks
        metadata: SecurityAssessmentMetadataProperties
        partners_data: SecurityAssessmentPartnerData
        resource_details: CommonResourceDetails
        risk: SecurityAssessmentPropertiesBaseRisk
        status: AssessmentStatusResponse

        @overload
        def __init__(
                self, 
                *, 
                additional_data: Optional[dict[str, str]] = ..., 
                metadata: Optional[SecurityAssessmentMetadataProperties] = ..., 
                partners_data: Optional[SecurityAssessmentPartnerData] = ..., 
                resource_details: CommonResourceDetails, 
                risk: Optional[SecurityAssessmentPropertiesBaseRisk] = ..., 
                status: AssessmentStatusResponse
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityAssessmentResponse(ExtensionResource):
        id: str
        name: str
        properties: Optional[SecurityAssessmentPropertiesResponse]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityAssessmentPropertiesResponse] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecurityConnector(ProxyResource):
        etag: Optional[str]
        id: str
        kind: Optional[str]
        location: Optional[str]
        name: str
        properties: Optional[SecurityConnectorProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SecurityConnectorProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecurityConnectorProperties(_Model):
        environment_data: Optional[EnvironmentData]
        environment_name: Optional[Union[str, CloudName]]
        hierarchy_identifier: Optional[str]
        hierarchy_identifier_trial_end_date: Optional[datetime]
        offerings: Optional[list[CloudOffering]]

        @overload
        def __init__(
                self, 
                *, 
                environment_data: Optional[EnvironmentData] = ..., 
                environment_name: Optional[Union[str, CloudName]] = ..., 
                hierarchy_identifier: Optional[str] = ..., 
                offerings: Optional[list[CloudOffering]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityContact(ProxyResource):
        id: str
        name: str
        properties: Optional[SecurityContactProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityContactProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecurityContactName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.security.models.SecurityContactProperties(_Model):
        emails: Optional[str]
        is_enabled: Optional[bool]
        notifications_by_role: Optional[SecurityContactPropertiesNotificationsByRole]
        notifications_sources: Optional[list[NotificationsSource]]
        phone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                emails: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                notifications_by_role: Optional[SecurityContactPropertiesNotificationsByRole] = ..., 
                notifications_sources: Optional[list[NotificationsSource]] = ..., 
                phone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityContactPropertiesNotificationsByRole(_Model):
        roles: Optional[list[Union[str, SecurityContactRole]]]
        state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                roles: Optional[list[Union[str, SecurityContactRole]]] = ..., 
                state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.security.models.SecurityOperator(ProxyResource):
        id: str
        identity: Optional[Identity]
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecuritySolution(ProxyResource):
        id: str
        location: str
        name: str
        properties: Optional[SecuritySolutionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecuritySolutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecuritySolutionProperties(_Model):
        protection_status: str
        provisioning_state: Union[str, ProvisioningState]
        security_family: Union[str, SecurityFamily]
        template: str

        @overload
        def __init__(
                self, 
                *, 
                protection_status: str, 
                provisioning_state: Union[str, ProvisioningState], 
                security_family: Union[str, SecurityFamily], 
                template: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecuritySolutionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.SecuritySolutionsReferenceData(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: SecuritySolutionsReferenceDataProperties
        system_data: Optional[SystemData]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: SecuritySolutionsReferenceDataProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecuritySolutionsReferenceDataList(_Model):
        value: Optional[list[SecuritySolutionsReferenceData]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SecuritySolutionsReferenceData]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecuritySolutionsReferenceDataProperties(_Model):
        alert_vendor_name: str
        package_info_url: str
        product_name: str
        publisher: str
        publisher_display_name: str
        security_family: Union[str, SecurityFamily]
        template: str

        @overload
        def __init__(
                self, 
                *, 
                alert_vendor_name: str, 
                package_info_url: str, 
                product_name: str, 
                publisher: str, 
                publisher_display_name: str, 
                security_family: Union[str, SecurityFamily], 
                template: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityStandard(ExtensionResource):
        id: str
        name: str
        properties: Optional[SecurityStandardProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityStandardProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecurityStandardProperties(_Model):
        assessments: Optional[list[PartialAssessmentProperties]]
        cloud_providers: Optional[list[Union[str, StandardSupportedCloud]]]
        description: Optional[str]
        display_name: Optional[str]
        metadata: Optional[StandardMetadata]
        policy_set_definition_id: Optional[str]
        standard_type: Optional[Union[str, StandardType]]

        @overload
        def __init__(
                self, 
                *, 
                assessments: Optional[list[PartialAssessmentProperties]] = ..., 
                cloud_providers: Optional[list[Union[str, StandardSupportedCloud]]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                metadata: Optional[StandardMetadata] = ..., 
                policy_set_definition_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecuritySubAssessment(ExtensionResource):
        id: str
        name: str
        properties: Optional[SecuritySubAssessmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecuritySubAssessmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecuritySubAssessmentProperties(_Model):
        additional_data: Optional[AdditionalData]
        category: Optional[str]
        description: Optional[str]
        display_name: Optional[str]
        id: Optional[str]
        impact: Optional[str]
        remediation: Optional[str]
        resource_details: Optional[CommonResourceDetails]
        status: Optional[SubAssessmentStatus]
        time_generated: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                additional_data: Optional[AdditionalData] = ..., 
                resource_details: Optional[CommonResourceDetails] = ..., 
                status: Optional[SubAssessmentStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SecurityTask(ProxyResource):
        id: str
        name: str
        properties: Optional[SecurityTaskProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityTaskProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.SecurityTaskParameters(_Model):
        name: Optional[str]


    class azure.mgmt.security.models.SecurityTaskProperties(_Model):
        creation_time_utc: Optional[datetime]
        last_state_change_time_utc: Optional[datetime]
        security_task_parameters: Optional[SecurityTaskParameters]
        state: Optional[str]
        sub_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                security_task_parameters: Optional[SecurityTaskParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SensitiveDataDiscoveryProperties(_Model):
        is_enabled: Optional[bool]
        operation_status: Optional[OperationStatus]
        scanner_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ..., 
                scanner_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SensitivityLabel(_Model):
        description: Optional[str]
        display_name: Optional[str]
        enabled: Optional[bool]
        order: Optional[int]
        rank: Optional[Union[str, Rank]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                order: Optional[int] = ..., 
                rank: Optional[Union[str, Rank]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ServerVulnerabilityAssessment(ProxyResource):
        id: str
        name: str
        properties: Optional[ServerVulnerabilityAssessmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServerVulnerabilityAssessmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentProperties(_Model):
        provisioning_state: Optional[Union[str, ServerVulnerabilityAssessmentPropertiesProvisioningState]]


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentPropertiesProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DEPROVISIONING = "Deprovisioning"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsAzureSettingProperties(_Model):
        selected_provider: Union[str, ServerVulnerabilityAssessmentsAzureSettingSelectedProvider]

        @overload
        def __init__(
                self, 
                *, 
                selected_provider: Union[str, ServerVulnerabilityAssessmentsAzureSettingSelectedProvider]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsAzureSettingSelectedProvider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MDE_TVM = "MdeTvm"


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsList(_Model):
        value: Optional[list[ServerVulnerabilityAssessment]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[ServerVulnerabilityAssessment]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsSetting(ProxyResource):
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


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsSettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVERS_SETTING = "AzureServersSetting"


    class azure.mgmt.security.models.ServerVulnerabilityAssessmentsSettingKindName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVERS_SETTING = "azureServersSetting"


    class azure.mgmt.security.models.ServerVulnerabilityProperties(AdditionalData, discriminator='ServerVulnerabilityAssessment'):
        assessed_resource_type: Literal[AssessedResourceType.SERVER_VULNERABILITY_ASSESSMENT]
        cve: Optional[list[_models.CVE]]
        cvss: Optional[dict[str, _models.CVSS]]
        patchable: Optional[bool]
        published_time: Optional[datetime]
        threat: Optional[str]
        type: Optional[str]
        vendor_references: Optional[list[VendorReference]]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.Setting(ProxyResource):
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


    class azure.mgmt.security.models.SettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_SUPPRESSION_SETTING = "AlertSuppressionSetting"
        ALERT_SYNC_SETTINGS = "AlertSyncSettings"
        DATA_EXPORT_SETTINGS = "DataExportSettings"


    class azure.mgmt.security.models.SettingName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT = "current"
        MCAS = "MCAS"
        SENTINEL = "Sentinel"
        WDATP = "WDATP"
        WDATP_EXCLUDE_LINUX_PUBLIC_PREVIEW = "WDATP_EXCLUDE_LINUX_PUBLIC_PREVIEW"
        WDATP_UNIFIED_SOLUTION = "WDATP_UNIFIED_SOLUTION"


    class azure.mgmt.security.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.SeverityEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.security.models.Source(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "Aws"
        AZURE = "Azure"
        GCP = "Gcp"
        ON_PREMISE = "OnPremise"
        ON_PREMISE_RESOURCE_DETAILS = "OnPremiseResourceDetails"
        ON_PREMISE_SQL = "OnPremiseSql"


    class azure.mgmt.security.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT = "Alert"
        ATTACK_PATH = "AttackPath"


    class azure.mgmt.security.models.SqlServerVulnerabilityProperties(AdditionalData, discriminator='SqlServerVulnerability'):
        assessed_resource_type: Literal[AssessedResourceType.SQL_SERVER_VULNERABILITY]
        query: Optional[str]
        type: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SqlVulnerabilityAssessmentScanOperationResult(Resource):
        id: str
        name: str
        properties: Optional[SqlVulnerabilityAssessmentScanOperationResultProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlVulnerabilityAssessmentScanOperationResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SqlVulnerabilityAssessmentScanOperationResultProperties(_Model):
        operation_id: Optional[str]
        scan_status: Optional[Union[str, ScanOperationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                scan_status: Optional[Union[str, ScanOperationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SqlVulnerabilityAssessmentSettings(ExtensionResource):
        id: str
        name: str
        properties: Optional[SqlVulnerabilityAssessmentSettingsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlVulnerabilityAssessmentSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SqlVulnerabilityAssessmentSettingsProperties(_Model):
        creation_time: Optional[datetime]
        state: Optional[Union[str, SqlVulnerabilityAssessmentState]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, SqlVulnerabilityAssessmentState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SqlVulnerabilityAssessmentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.Standard(ProxyResource):
        etag: Optional[str]
        id: str
        kind: Optional[str]
        location: Optional[str]
        name: str
        properties: Optional[StandardProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[StandardProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.StandardAssignment(ExtensionResource):
        id: str
        name: str
        properties: Optional[StandardAssignmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StandardAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.StandardAssignmentMetadata(_Model):
        created_by: Optional[str]
        created_on: Optional[datetime]
        last_updated_by: Optional[str]
        last_updated_on: Optional[datetime]


    class azure.mgmt.security.models.StandardAssignmentProperties(_Model):
        assigned_standard: Optional[AssignedStandardItem]
        attestation_data: Optional[StandardAssignmentPropertiesAttestationData]
        description: Optional[str]
        display_name: Optional[str]
        effect: Optional[Union[str, Effect]]
        excluded_scopes: Optional[list[str]]
        exemption_data: Optional[StandardAssignmentPropertiesExemptionData]
        expires_on: Optional[datetime]
        metadata: Optional[StandardAssignmentMetadata]

        @overload
        def __init__(
                self, 
                *, 
                assigned_standard: Optional[AssignedStandardItem] = ..., 
                attestation_data: Optional[StandardAssignmentPropertiesAttestationData] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                effect: Optional[Union[str, Effect]] = ..., 
                excluded_scopes: Optional[list[str]] = ..., 
                exemption_data: Optional[StandardAssignmentPropertiesExemptionData] = ..., 
                expires_on: Optional[datetime] = ..., 
                metadata: Optional[StandardAssignmentMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.StandardAssignmentPropertiesAttestationData(_Model):
        assigned_assessment: Optional[AssignedAssessmentItem]
        compliance_date: Optional[datetime]
        compliance_state: Optional[Union[str, AttestationComplianceState]]
        evidence: Optional[list[AttestationEvidence]]

        @overload
        def __init__(
                self, 
                *, 
                assigned_assessment: Optional[AssignedAssessmentItem] = ..., 
                compliance_state: Optional[Union[str, AttestationComplianceState]] = ..., 
                evidence: Optional[list[AttestationEvidence]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.StandardAssignmentPropertiesExemptionData(_Model):
        assigned_assessment: Optional[AssignedAssessmentItem]
        exemption_category: Optional[Union[str, ExemptionCategory]]

        @overload
        def __init__(
                self, 
                *, 
                assigned_assessment: Optional[AssignedAssessmentItem] = ..., 
                exemption_category: Optional[Union[str, ExemptionCategory]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.StandardComponentProperties(_Model):
        key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.StandardMetadata(_Model):
        created_by: Optional[str]
        created_on: Optional[datetime]
        last_updated_by: Optional[str]
        last_updated_on: Optional[datetime]


    class azure.mgmt.security.models.StandardProperties(_Model):
        category: Optional[str]
        components: Optional[list[StandardComponentProperties]]
        description: Optional[str]
        display_name: Optional[str]
        standard_type: Optional[str]
        supported_clouds: Optional[list[Union[str, StandardSupportedClouds]]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                components: Optional[list[StandardComponentProperties]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                supported_clouds: Optional[list[Union[str, StandardSupportedClouds]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.StandardSupportedCloud(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "AWS"
        AZURE = "Azure"
        GCP = "GCP"


    class azure.mgmt.security.models.StandardSupportedClouds(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "AWS"
        GCP = "GCP"


    class azure.mgmt.security.models.StandardType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANCE = "Compliance"
        CUSTOM = "Custom"
        DEFAULT = "Default"


    class azure.mgmt.security.models.StartMalwareScanRequest(_Model):
        properties: Optional[StartMalwareScanRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StartMalwareScanRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.StartMalwareScanRequestProperties(_Model):
        filters: Optional[MalwareScanFilters]

        @overload
        def __init__(
                self, 
                *, 
                filters: Optional[MalwareScanFilters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        OFF = "Off"
        ON = "On"
        PASSED = "Passed"
        SKIPPED = "Skipped"
        UNSUPPORTED = "Unsupported"


    class azure.mgmt.security.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INITIATED = "Initiated"
        REVOKED = "Revoked"


    class azure.mgmt.security.models.StatusAutoGenerated(_Model):
        code: Optional[Union[str, StatusName]]
        first_evaluation_date: Optional[datetime]
        last_scanned_date: Optional[datetime]
        reason: Optional[str]
        status_change_date: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, StatusName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.StatusName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_APPLICABLE = "NotApplicable"
        NOT_HEALTHY = "NotHealthy"


    class azure.mgmt.security.models.StatusReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPIRED = "Expired"
        NEWER_REQUEST_INITIATED = "NewerRequestInitiated"
        USER_REQUESTED = "UserRequested"


    class azure.mgmt.security.models.SubAssessmentStatus(_Model):
        cause: Optional[str]
        code: Optional[Union[str, SubAssessmentStatusCode]]
        description: Optional[str]
        severity: Optional[Union[str, Severity]]


    class azure.mgmt.security.models.SubAssessmentStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_APPLICABLE = "NotApplicable"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.security.models.SubPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1 = "P1"
        P2 = "P2"


    class azure.mgmt.security.models.SuppressionAlertsScope(_Model):
        all_of: list[ScopeElement]

        @overload
        def __init__(
                self, 
                *, 
                all_of: list[ScopeElement]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.SystemData(_Model):
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


    class azure.mgmt.security.models.Tags(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.TagsResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.TargetBranchConfiguration(_Model):
        annotate_default_branch: Optional[Union[str, AnnotateDefaultBranchState]]
        branch_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                annotate_default_branch: Optional[Union[str, AnnotateDefaultBranchState]] = ..., 
                branch_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.security.models.ThresholdCustomAlertRule(CustomAlertRule, discriminator='ThresholdCustomAlertRule'):
        description: str
        display_name: str
        is_enabled: bool
        max_threshold: int
        min_threshold: int
        rule_type: Literal["ThresholdCustomAlertRule"]

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                max_threshold: int, 
                min_threshold: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.TimeWindowCustomAlertRule(ThresholdCustomAlertRule, discriminator='TimeWindowCustomAlertRule'):
        rule_type: Literal["TimeWindowCustomAlertRule"]
        time_window_size: timedelta

        @overload
        def __init__(
                self, 
                *, 
                time_window_size: timedelta
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.TopologyResource(ProxyResource):
        id: str
        location: str
        name: str
        properties: Optional[TopologyResourceProperties]
        system_data: SystemData
        type: str


    class azure.mgmt.security.models.TopologyResourceProperties(_Model):
        calculated_date_time: Optional[datetime]
        topology_resources: Optional[list[TopologySingleResource]]


    class azure.mgmt.security.models.TopologySingleResource(_Model):
        children: Optional[list[TopologySingleResourceChild]]
        location: Optional[str]
        network_zones: Optional[str]
        parents: Optional[list[TopologySingleResourceParent]]
        recommendations_exist: Optional[bool]
        resource_id: Optional[str]
        severity: Optional[str]
        topology_score: Optional[int]


    class azure.mgmt.security.models.TopologySingleResourceChild(_Model):
        resource_id: Optional[str]


    class azure.mgmt.security.models.TopologySingleResourceParent(_Model):
        resource_id: Optional[str]


    class azure.mgmt.security.models.TrackedResource(Resource):
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


    class azure.mgmt.security.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUALYS = "Qualys"
        TVM = "TVM"


    class azure.mgmt.security.models.UnmaskedIpLoggingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.security.models.UpdateIoTSecuritySolutionProperties(_Model):
        recommendations_configuration: Optional[list[RecommendationConfigurationProperties]]
        user_defined_resources: Optional[UserDefinedResourcesProperties]

        @overload
        def __init__(
                self, 
                *, 
                recommendations_configuration: Optional[list[RecommendationConfigurationProperties]] = ..., 
                user_defined_resources: Optional[UserDefinedResourcesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.UpdateIotSecuritySolutionData(TagsResource):
        properties: Optional[UpdateIoTSecuritySolutionProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateIoTSecuritySolutionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.UpdateSensitivitySettingsRequest(_Model):
        sensitive_info_types_ids: list[str]
        sensitivity_threshold_label_id: Optional[str]
        sensitivity_threshold_label_order: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                sensitive_info_types_ids: list[str], 
                sensitivity_threshold_label_id: Optional[str] = ..., 
                sensitivity_threshold_label_order: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.UserDefinedResourcesProperties(_Model):
        query: str
        query_subscriptions: list[str]

        @overload
        def __init__(
                self, 
                *, 
                query: str, 
                query_subscriptions: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.UserImpact(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MODERATE = "Moderate"


    class azure.mgmt.security.models.VaRule(_Model):
        benchmark_references: Optional[list[BenchmarkReference]]
        category: Optional[str]
        description: Optional[str]
        query_check: Optional[QueryCheck]
        rationale: Optional[str]
        rule_id: Optional[str]
        rule_type: Optional[Union[str, RuleType]]
        severity: Optional[Union[str, RuleSeverity]]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                benchmark_references: Optional[list[BenchmarkReference]] = ..., 
                category: Optional[str] = ..., 
                description: Optional[str] = ..., 
                query_check: Optional[QueryCheck] = ..., 
                rationale: Optional[str] = ..., 
                rule_id: Optional[str] = ..., 
                rule_type: Optional[Union[str, RuleType]] = ..., 
                severity: Optional[Union[str, RuleSeverity]] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.ValueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IP_CIDR = "IpCidr"
        STRING = "String"


    class azure.mgmt.security.models.VendorReference(_Model):
        link: Optional[str]
        title: Optional[str]


    class azure.mgmt.security.models.VmScannersAws(VmScannersBase):
        cloud_role_arn: Optional[str]
        configuration: VmScannersBaseConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                cloud_role_arn: Optional[str] = ..., 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.VmScannersBase(_Model):
        configuration: Optional[VmScannersBaseConfiguration]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.VmScannersBaseConfiguration(_Model):
        exclusion_tags: Optional[dict[str, str]]
        scanning_mode: Optional[Union[str, ScanningMode]]

        @overload
        def __init__(
                self, 
                *, 
                exclusion_tags: Optional[dict[str, str]] = ..., 
                scanning_mode: Optional[Union[str, ScanningMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.VmScannersGcp(VmScannersBase):
        configuration: VmScannersBaseConfiguration
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[VmScannersBaseConfiguration] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.security.models.WorkspaceSetting(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkspaceSettingProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkspaceSettingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.security.models.WorkspaceSettingProperties(_Model):
        scope: str
        workspace_id: str

        @overload
        def __init__(
                self, 
                *, 
                scope: str, 
                workspace_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
                resource_group_name: str, 
                asc_location: str, 
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
                *, 
                alert_type: Optional[str] = ..., 
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
                *, 
                expand: Optional[Union[str, ExpandEnum]] = ..., 
                **kwargs: Any
            ) -> SecurityAssessmentResponse: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[SecurityAssessmentResponse]: ...


    class azure.mgmt.security.operations.AssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                assignment_id: str, 
                assignment: Assignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Assignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                assignment_id: str, 
                assignment: Assignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Assignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                assignment_id: str, 
                assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Assignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                assignment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                assignment_id: str, 
                **kwargs: Any
            ) -> Assignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Assignment]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Assignment]: ...


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


    class azure.mgmt.security.operations.BatchPricingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                scope_id: str, 
                pricing_batch_name: str, 
                pricing_batch: PricingBatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PricingBatch: ...

        @overload
        def create_or_update(
                self, 
                scope_id: str, 
                pricing_batch_name: str, 
                pricing_batch: PricingBatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PricingBatch: ...

        @overload
        def create_or_update(
                self, 
                scope_id: str, 
                pricing_batch_name: str, 
                pricing_batch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PricingBatch: ...

        @distributed_trace
        def get(
                self, 
                scope_id: str, 
                pricing_batch_name: str, 
                **kwargs: Any
            ) -> PricingBatch: ...

        @distributed_trace
        def list(
                self, 
                scope_id: str, 
                **kwargs: Any
            ) -> ItemPaged[PricingBatch]: ...


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
                setting_name: str, 
                scan_id: str, 
                **kwargs: Any
            ) -> MalwareScan: ...

        @overload
        def create(
                self, 
                resource_id: str, 
                setting_name: str, 
                defender_for_storage_setting: DefenderForStorageSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @overload
        def create(
                self, 
                resource_id: str, 
                setting_name: str, 
                defender_for_storage_setting: DefenderForStorageSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @overload
        def create(
                self, 
                resource_id: str, 
                setting_name: str, 
                defender_for_storage_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @distributed_trace
        def get(
                self, 
                resource_id: str, 
                setting_name: str, 
                **kwargs: Any
            ) -> DefenderForStorageSetting: ...

        @distributed_trace
        def get_malware_scan(
                self, 
                resource_id: str, 
                setting_name: str, 
                scan_id: str, 
                **kwargs: Any
            ) -> MalwareScan: ...

        @distributed_trace
        def list(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> ItemPaged[DefenderForStorageSetting]: ...

        @overload
        def start_malware_scan(
                self, 
                resource_id: str, 
                setting_name: str, 
                body: Optional[StartMalwareScanRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MalwareScan: ...

        @overload
        def start_malware_scan(
                self, 
                resource_id: str, 
                setting_name: str, 
                body: Optional[StartMalwareScanRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MalwareScan: ...

        @overload
        def start_malware_scan(
                self, 
                resource_id: str, 
                setting_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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


    class azure.mgmt.security.operations.GitHubIssuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                repo_name: str, 
                create_issue_request: Optional[IssueCreationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                repo_name: str, 
                create_issue_request: Optional[IssueCreationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                security_connector_name: str, 
                owner_name: str, 
                repo_name: str, 
                create_issue_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[IoTSecuritySolutionModel]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
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
                *, 
                top: Optional[int] = ..., 
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
                *, 
                top: Optional[int] = ..., 
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


    class azure.mgmt.security.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.security.operations.OperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


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
                *, 
                filter: Optional[str] = ..., 
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
                private_link_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
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
                private_link_name: str, 
                group_id: str, 
                **kwargs: Any
            ) -> PrivateLinkGroupResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkGroupResource]: ...


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
                private_link_name: str, 
                private_link: PrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateLinkResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_link: PrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateLinkResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_link: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateLinkResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def head(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
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
                private_link_name: str, 
                private_link: PrivateLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
                private_link: PrivateLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                private_link_name: str, 
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
                *, 
                filter: Optional[str] = ..., 
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
                *, 
                filter: Optional[str] = ..., 
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
                *, 
                filter: Optional[str] = ..., 
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
                *, 
                expand: Optional[Union[str, ExpandControlsEnum]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SecureScoreControlDetails]: ...

        @distributed_trace
        def list_by_secure_score(
                self, 
                secure_score_name: str, 
                *, 
                expand: Optional[Union[str, ExpandControlsEnum]] = ..., 
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
            ) -> ItemPaged[SecurityOperator]: ...


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
                setting_name: Union[str, SettingName], 
                **kwargs: Any
            ) -> Setting: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Setting]: ...

        @overload
        def update(
                self, 
                setting_name: Union[str, SettingName], 
                setting: Setting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @overload
        def update(
                self, 
                setting_name: Union[str, SettingName], 
                setting: Setting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @overload
        def update(
                self, 
                setting_name: Union[str, SettingName], 
                setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...


    class azure.mgmt.security.operations.SqlVulnerabilityAssessmentBaselineRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def add(
                self, 
                resource_id: str, 
                body: Optional[RulesResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RulesResults: ...

        @overload
        def add(
                self, 
                resource_id: str, 
                body: Optional[RulesResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RulesResults: ...

        @overload
        def add(
                self, 
                resource_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RulesResults: ...

        @overload
        def create_or_update(
                self, 
                resource_id: str, 
                rule_id: str, 
                body: Optional[RuleResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleResults: ...

        @overload
        def create_or_update(
                self, 
                resource_id: str, 
                rule_id: str, 
                body: Optional[RuleResultsInput] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleResults: ...

        @overload
        def create_or_update(
                self, 
                resource_id: str, 
                rule_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleResults: ...

        @distributed_trace
        def delete(
                self, 
                resource_id: str, 
                rule_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_id: str, 
                rule_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleResults: ...

        @distributed_trace
        def list(
                self, 
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RuleResults]: ...


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
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> ScanResult: ...

        @distributed_trace
        def list(
                self, 
                scan_id: str, 
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ScanResult]: ...


    class azure.mgmt.security.operations.SqlVulnerabilityAssessmentScansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_initiate_scan(
                self, 
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[SqlVulnerabilityAssessmentScanOperationResult]: ...

        @distributed_trace
        def get(
                self, 
                scan_id: str, 
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> ScanV2: ...

        @distributed_trace
        def get_scan_operation_result(
                self, 
                resource_id: str, 
                operation_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> SqlVulnerabilityAssessmentScanOperationResult: ...

        @distributed_trace
        def list(
                self, 
                resource_id: str, 
                *, 
                database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ScanV2]: ...


    class azure.mgmt.security.operations.SqlVulnerabilityAssessmentSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_id: str, 
                body: Optional[SqlVulnerabilityAssessmentSettings] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlVulnerabilityAssessmentSettings: ...

        @overload
        def create_or_update(
                self, 
                resource_id: str, 
                body: Optional[SqlVulnerabilityAssessmentSettings] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlVulnerabilityAssessmentSettings: ...

        @overload
        def create_or_update(
                self, 
                resource_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlVulnerabilityAssessmentSettings: ...

        @distributed_trace
        def delete(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> SqlVulnerabilityAssessmentSettings: ...


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


    class azure.mgmt.security.operations.StandardsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                standard_id: str, 
                standard: Standard, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Standard: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                standard_id: str, 
                standard: Standard, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Standard: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                standard_id: str, 
                standard: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Standard: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                standard_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                standard_id: str, 
                **kwargs: Any
            ) -> Standard: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Standard]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Standard]: ...


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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SecurityTask]: ...

        @distributed_trace
        def list_by_home_region(
                self, 
                asc_location: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SecurityTask]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                asc_location: str, 
                *, 
                filter: Optional[str] = ..., 
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
        def list(self, **kwargs: Any) -> ItemPaged[TopologyResource]: ...


    class azure.mgmt.security.operations.TopologyResourcesOperations:

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


namespace azure.mgmt.security.types

    class azure.mgmt.security.types.AccessTokenAuthentication(TypedDict, total=False):
        key "accessToken": str
        key "authenticationType": Required[Literal[AuthenticationType.ACCESS_TOKEN]]
        key "username": str
        accessToken: str
        authenticationType: Literal[AuthenticationType.ACCESS_TOKEN]
        username: str


    class azure.mgmt.security.types.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_HUB = "EventHub"
        INTERNAL = "Internal"
        LOGIC_APP = "LogicApp"
        WORKSPACE = "Workspace"


    class azure.mgmt.security.types.ActionableRemediation(TypedDict, total=False):
        key "branchConfiguration": ForwardRef('TargetBranchConfiguration', module='types')
        key "inheritFromParentState": Union[str, InheritFromParentState]
        key "state": Union[str, ActionableRemediationState]
        branchConfiguration: TargetBranchConfiguration
        categoryConfigurations: list[CategoryConfiguration]
        inheritFromParentState: Union[str, InheritFromParentState]
        state: Union[str, ActionableRemediationState]


    class azure.mgmt.security.types.AdditionalWorkspacesProperties(TypedDict, total=False):
        key "type": Union[str, AdditionalWorkspaceType]
        key "workspace": str
        dataTypes: list[Union[str, AdditionalWorkspaceDataType]]
        type: Union[str, AdditionalWorkspaceType]
        workspace: str


    class azure.mgmt.security.types.AdvancedThreatProtectionProperties(TypedDict, total=False):
        key "isEnabled": bool
        isEnabled: bool


    class azure.mgmt.security.types.AdvancedThreatProtectionSetting(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AdvancedThreatProtectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AdvancedThreatProtectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.AgentlessConfiguration(TypedDict, total=False):
        key "agentlessAutoDiscovery": Union[str, AutoDiscovery]
        key "agentlessEnabled": Union[str, AgentlessEnablement]
        key "inventoryListType": Union[str, InventoryListKind]
        agentlessAutoDiscovery: Union[str, AutoDiscovery]
        agentlessEnabled: Union[str, AgentlessEnablement]
        inventoryList: list[InventoryList]
        inventoryListType: Union[str, InventoryListKind]
        scanners: list[str]


    class azure.mgmt.security.types.AlertSimulatorBundlesRequestProperties(TypedDict, total=False):
        key "kind": Required[Literal[KindEnum.BUNDLES]]
        bundles: list[Union[str, BundleType]]
        kind: Literal[KindEnum.BUNDLES]


    class azure.mgmt.security.types.AlertSimulatorRequestBody(TypedDict, total=False):
        key "properties": ForwardRef('AlertSimulatorRequestProperties', module='types')
        properties: AlertSimulatorRequestProperties


    class azure.mgmt.security.types.AlertSimulatorRequestProperties(TypedDict, total=False):
        key "kind": Required[Literal[KindEnum.BUNDLES]]
        bundles: list[Union[str, BundleType]]
        kind: Literal[KindEnum.BUNDLES]


    class azure.mgmt.security.types.AlertSyncSettingProperties(TypedDict, total=False):
        key "enabled": Required[bool]
        enabled: bool


    class azure.mgmt.security.types.AlertSyncSettings(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[SettingKind.ALERT_SYNC_SETTINGS]]
        key "name": str
        key "properties": ForwardRef('AlertSyncSettingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[SettingKind.ALERT_SYNC_SETTINGS]
        name: str
        properties: AlertSyncSettingProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.AlertsSuppressionRule(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AlertsSuppressionRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AlertsSuppressionRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.AlertsSuppressionRuleProperties(TypedDict, total=False):
        key "alertType": Required[str]
        key "comment": str
        key "expirationDateUtc": str
        key "lastModifiedUtc": str
        key "reason": Required[str]
        key "state": Required[Union[str, RuleState]]
        key "suppressionAlertsScope": ForwardRef('SuppressionAlertsScope', module='types')
        alertType: str
        comment: str
        expirationDateUtc: str
        lastModifiedUtc: str
        reason: str
        state: Union[str, RuleState]
        suppressionAlertsScope: SuppressionAlertsScope


    class azure.mgmt.security.types.AllowlistCustomAlertRule(TypedDict, total=False):
        key "allowlistValues": Required[list[str]]
        key "description": str
        key "displayName": str
        key "isEnabled": Required[bool]
        key "ruleType": Required[Literal["AllowlistCustomAlertRule"]]
        key "valueType": Union[str, ValueType]
        allowlistValues: list[str]
        description: str
        displayName: str
        isEnabled: bool
        ruleType: Literal[AllowlistCustomAlertRule]
        valueType: Union[str, ValueType]


    class azure.mgmt.security.types.Application(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ApplicationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ApplicationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.ApplicationProperties(TypedDict, total=False):
        key "conditionSets": Required[list[Any]]
        key "description": str
        key "displayName": str
        key "sourceResourceType": Required[Union[str, ApplicationSourceResourceType]]
        conditionSets: list[Any]
        description: str
        displayName: str
        sourceResourceType: Union[str, ApplicationSourceResourceType]


    class azure.mgmt.security.types.ArcAutoProvisioning(TypedDict, total=False):
        key "configuration": ForwardRef('ArcAutoProvisioningConfiguration', module='types')
        key "enabled": bool
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool


    class azure.mgmt.security.types.ArcAutoProvisioningAws(ArcAutoProvisioning):
        key "cloudRoleArn": str
        key "configuration": ForwardRef('ArcAutoProvisioningConfiguration', module='types')
        key "enabled": bool
        cloudRoleArn: str
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool


    class azure.mgmt.security.types.ArcAutoProvisioningConfiguration(TypedDict, total=False):
        key "privateLinkScope": str
        key "proxy": str
        privateLinkScope: str
        proxy: str


    class azure.mgmt.security.types.ArcAutoProvisioningGcp(ArcAutoProvisioning):
        key "configuration": ForwardRef('ArcAutoProvisioningConfiguration', module='types')
        key "enabled": bool
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool


    class azure.mgmt.security.types.AssessmentLinks(TypedDict, total=False):
        key "azurePortalUri": str
        azurePortalUri: str


    class azure.mgmt.security.types.AssessmentStatus(TypedDict, total=False):
        key "cause": str
        key "code": Required[Union[str, AssessmentStatusCode]]
        key "description": str
        cause: str
        code: Union[str, AssessmentStatusCode]
        description: str


    class azure.mgmt.security.types.AssignedAssessmentItem(TypedDict, total=False):
        key "assessmentKey": str
        assessmentKey: str


    class azure.mgmt.security.types.AssignedComponentItem(TypedDict, total=False):
        key "key": str
        key: str


    class azure.mgmt.security.types.AssignedStandardItem(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.security.types.Assignment(ProxyResource):
        key "etag": str
        key "id": str
        key "kind": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('AssignmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: str
        location: str
        name: str
        properties: AssignmentProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.security.types.AssignmentProperties(TypedDict, total=False):
        key "additionalData": ForwardRef('AssignmentPropertiesAdditionalData', module='types')
        key "assignedComponent": ForwardRef('AssignedComponentItem', module='types')
        key "assignedStandard": ForwardRef('AssignedStandardItem', module='types')
        key "description": str
        key "displayName": str
        key "effect": str
        key "expiresOn": str
        key "metadata": Any
        key "scope": str
        additionalData: AssignmentPropertiesAdditionalData
        assignedComponent: AssignedComponentItem
        assignedStandard: AssignedStandardItem
        description: str
        displayName: str
        effect: str
        expiresOn: str
        metadata: Any
        scope: str


    class azure.mgmt.security.types.AssignmentPropertiesAdditionalData(TypedDict, total=False):
        key "exemptionCategory": str
        exemptionCategory: str


    class azure.mgmt.security.types.AttestationEvidence(TypedDict, total=False):
        key "description": str
        key "sourceUrl": str
        description: str
        sourceUrl: str


    class azure.mgmt.security.types.Authentication(TypedDict, total=False):
        key "accessToken": str
        key "authenticationType": Required[Literal[AuthenticationType.ACCESS_TOKEN]]
        key "username": str
        accessToken: str
        authenticationType: Literal[AuthenticationType.ACCESS_TOKEN]
        username: str


    class azure.mgmt.security.types.AuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_TOKEN = "AccessToken"


    class azure.mgmt.security.types.Authorization(TypedDict, total=False):
        key "code": str
        code: str


    class azure.mgmt.security.types.AutoProvisioningSetting(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AutoProvisioningSettingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AutoProvisioningSettingProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.AutoProvisioningSettingProperties(TypedDict, total=False):
        key "autoProvision": Required[Union[str, AutoProvision]]
        autoProvision: Union[str, AutoProvision]


    class azure.mgmt.security.types.Automation(ProxyResource):
        key "etag": str
        key "id": str
        key "kind": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('AutomationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: str
        location: str
        name: str
        properties: AutomationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.security.types.AutomationActionEventHub(TypedDict, total=False):
        key "actionType": Required[Literal[ActionType.EVENT_HUB]]
        key "connectionString": str
        key "eventHubResourceId": str
        key "isTrustedServiceEnabled": bool
        key "sasPolicyName": str
        actionType: Literal[ActionType.EVENT_HUB]
        connectionString: str
        eventHubResourceId: str
        isTrustedServiceEnabled: bool
        sasPolicyName: str


    class azure.mgmt.security.types.AutomationActionLogicApp(TypedDict, total=False):
        key "actionType": Required[Literal[ActionType.LOGIC_APP]]
        key "logicAppResourceId": str
        key "uri": str
        actionType: Literal[ActionType.LOGIC_APP]
        logicAppResourceId: str
        uri: str


    class azure.mgmt.security.types.AutomationActionWorkspace(TypedDict, total=False):
        key "actionType": Required[Literal[ActionType.WORKSPACE]]
        key "workspaceResourceId": str
        actionType: Literal[ActionType.WORKSPACE]
        workspaceResourceId: str


    class azure.mgmt.security.types.AutomationProperties(TypedDict, total=False):
        key "description": str
        key "isEnabled": bool
        actions: list[AutomationAction]
        description: str
        isEnabled: bool
        scopes: list[AutomationScope]
        sources: list[AutomationSource]


    class azure.mgmt.security.types.AutomationRuleSet(TypedDict, total=False):
        rules: list[AutomationTriggeringRule]


    class azure.mgmt.security.types.AutomationScope(TypedDict, total=False):
        key "description": str
        key "scopePath": str
        description: str
        scopePath: str


    class azure.mgmt.security.types.AutomationSource(TypedDict, total=False):
        key "eventSource": Union[str, EventSource]
        eventSource: Union[str, EventSource]
        ruleSets: list[AutomationRuleSet]


    class azure.mgmt.security.types.AutomationTriggeringRule(TypedDict, total=False):
        key "expectedValue": str
        key "operator": Union[str, Operator]
        key "propertyJPath": str
        key "propertyType": Union[str, PropertyType]
        expectedValue: str
        operator: Union[str, Operator]
        propertyJPath: str
        propertyType: Union[str, PropertyType]


    class azure.mgmt.security.types.AutomationUpdateModel(Tags):
        key "properties": ForwardRef('AutomationProperties', module='types')
        properties: AutomationProperties
        tags: dict[str, str]


    class azure.mgmt.security.types.AwsCloudTrailConfiguration(TypedDict, total=False):
        key "deploymentRegion": str
        key "provisioningType": Union[str, AwsCloudTrailProvisioningType]
        key "resourceNamePrefix": str
        cloudTrailResourceSets: list[AwsCloudTrailResourceSet]
        deploymentRegion: str
        provisioningType: Union[str, AwsCloudTrailProvisioningType]
        resourceNamePrefix: str


    class azure.mgmt.security.types.AwsCloudTrailResourceSet(TypedDict, total=False):
        key "kmsKeyArn": str
        key "resourceRegion": str
        key "s3BucketArn": str
        key "sqsQueueArn": str
        kmsKeyArn: str
        resourceRegion: str
        s3BucketArn: str
        sqsQueueArn: str


    class azure.mgmt.security.types.AwsEnvironmentData(TypedDict, total=False):
        key "accountName": str
        key "environmentType": Required[Literal[EnvironmentType.AWS_ACCOUNT]]
        key "organizationalData": ForwardRef('AwsOrganizationalData', module='types')
        key "scanInterval": int
        accountName: str
        environmentType: Literal[EnvironmentType.AWS_ACCOUNT]
        organizationalData: AwsOrganizationalData
        regions: list[str]
        scanInterval: int


    class azure.mgmt.security.types.AwsOrganizationalDataMaster(TypedDict, total=False):
        key "organizationMembershipType": Required[Literal[OrganizationMembershipType.ORGANIZATION]]
        key "stacksetName": str
        excludedAccountIds: list[str]
        organizationMembershipType: Literal[OrganizationMembershipType.ORGANIZATION]
        stacksetName: str


    class azure.mgmt.security.types.AwsOrganizationalDataMember(TypedDict, total=False):
        key "organizationMembershipType": Required[Literal[OrganizationMembershipType.MEMBER]]
        key "parentHierarchyId": str
        organizationMembershipType: Literal[OrganizationMembershipType.MEMBER]
        parentHierarchyId: str


    class azure.mgmt.security.types.AzureDevOpsOrg(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AzureDevOpsOrgProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AzureDevOpsOrgProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.AzureDevOpsOrgProperties(TypedDict, total=False):
        key "actionableRemediation": ForwardRef('ActionableRemediation', module='types')
        key "onboardingState": Union[str, OnboardingState]
        key "provisioningState": Union[str, DevOpsProvisioningState]
        key "provisioningStatusMessage": str
        key "provisioningStatusUpdateTimeUtc": str
        actionableRemediation: ActionableRemediation
        onboardingState: Union[str, OnboardingState]
        provisioningState: Union[str, DevOpsProvisioningState]
        provisioningStatusMessage: str
        provisioningStatusUpdateTimeUtc: str


    class azure.mgmt.security.types.AzureDevOpsProject(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AzureDevOpsProjectProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AzureDevOpsProjectProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.AzureDevOpsProjectProperties(TypedDict, total=False):
        key "actionableRemediation": ForwardRef('ActionableRemediation', module='types')
        key "onboardingState": Union[str, OnboardingState]
        key "parentOrgName": str
        key "projectId": str
        key "provisioningState": Union[str, DevOpsProvisioningState]
        key "provisioningStatusMessage": str
        key "provisioningStatusUpdateTimeUtc": str
        actionableRemediation: ActionableRemediation
        onboardingState: Union[str, OnboardingState]
        parentOrgName: str
        projectId: str
        provisioningState: Union[str, DevOpsProvisioningState]
        provisioningStatusMessage: str
        provisioningStatusUpdateTimeUtc: str


    class azure.mgmt.security.types.AzureDevOpsRepository(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AzureDevOpsRepositoryProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AzureDevOpsRepositoryProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.AzureDevOpsRepositoryProperties(TypedDict, total=False):
        key "actionableRemediation": ForwardRef('ActionableRemediation', module='types')
        key "onboardingState": Union[str, OnboardingState]
        key "parentOrgName": str
        key "parentProjectName": str
        key "provisioningState": Union[str, DevOpsProvisioningState]
        key "provisioningStatusMessage": str
        key "provisioningStatusUpdateTimeUtc": str
        key "repoId": str
        key "repoUrl": str
        key "visibility": str
        actionableRemediation: ActionableRemediation
        onboardingState: Union[str, OnboardingState]
        parentOrgName: str
        parentProjectName: str
        provisioningState: Union[str, DevOpsProvisioningState]
        provisioningStatusMessage: str
        provisioningStatusUpdateTimeUtc: str
        repoId: str
        repoUrl: str
        visibility: str


    class azure.mgmt.security.types.AzureDevOpsScopeEnvironmentData(TypedDict, total=False):
        key "environmentType": Required[Literal[EnvironmentType.AZURE_DEV_OPS_SCOPE]]
        environmentType: Literal[EnvironmentType.AZURE_DEV_OPS_SCOPE]


    class azure.mgmt.security.types.AzureResourceDetails(TypedDict, total=False):
        key "id": str
        key "source": Required[Literal[Source.AZURE]]
        id: str
        source: Literal[Source.AZURE]


    class azure.mgmt.security.types.AzureServersSetting(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[ServerVulnerabilityAssessmentsSettingKind.AZURE_SERVERS_SETTING]]
        key "name": str
        key "properties": ForwardRef('ServerVulnerabilityAssessmentsAzureSettingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[ServerVulnerabilityAssessmentsSettingKind.AZURE_SERVERS_SETTING]
        name: str
        properties: ServerVulnerabilityAssessmentsAzureSettingProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.BlobScanFilter(TypedDict, total=False):
        key "blob": ForwardRef('MatchFilter', module='types')
        key "container": ForwardRef('MatchFilter', module='types')
        blob: MatchFilter
        container: MatchFilter


    class azure.mgmt.security.types.CategoryConfiguration(TypedDict, total=False):
        key "category": Union[str, RuleCategory]
        key "minimumSeverityLevel": str
        category: Union[str, RuleCategory]
        minimumSeverityLevel: str


    class azure.mgmt.security.types.CspmMonitorAwsOffering(TypedDict, total=False):
        key "description": str
        key "nativeCloudConnection": ForwardRef('CspmMonitorAwsOfferingNativeCloudConnection', module='types')
        key "offeringType": Required[Literal[OfferingType.CSPM_MONITOR_AWS]]
        description: str
        nativeCloudConnection: CspmMonitorAwsOfferingNativeCloudConnection
        offeringType: Literal[OfferingType.CSPM_MONITOR_AWS]


    class azure.mgmt.security.types.CspmMonitorAwsOfferingNativeCloudConnection(TypedDict, total=False):
        key "cloudRoleArn": str
        cloudRoleArn: str


    class azure.mgmt.security.types.CspmMonitorAzureDevOpsOffering(TypedDict, total=False):
        key "description": str
        key "offeringType": Required[Literal[OfferingType.CSPM_MONITOR_AZURE_DEV_OPS]]
        description: str
        offeringType: Literal[OfferingType.CSPM_MONITOR_AZURE_DEV_OPS]


    class azure.mgmt.security.types.CspmMonitorDockerHubOffering(TypedDict, total=False):
        key "description": str
        key "offeringType": Required[Literal[OfferingType.CSPM_MONITOR_DOCKER_HUB]]
        description: str
        offeringType: Literal[OfferingType.CSPM_MONITOR_DOCKER_HUB]


    class azure.mgmt.security.types.CspmMonitorGcpOffering(TypedDict, total=False):
        key "description": str
        key "nativeCloudConnection": ForwardRef('CspmMonitorGcpOfferingNativeCloudConnection', module='types')
        key "offeringType": Required[Literal[OfferingType.CSPM_MONITOR_GCP]]
        description: str
        nativeCloudConnection: CspmMonitorGcpOfferingNativeCloudConnection
        offeringType: Literal[OfferingType.CSPM_MONITOR_GCP]


    class azure.mgmt.security.types.CspmMonitorGcpOfferingNativeCloudConnection(TypedDict, total=False):
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.CspmMonitorGitLabOffering(TypedDict, total=False):
        key "description": str
        key "offeringType": Required[Literal[OfferingType.CSPM_MONITOR_GIT_LAB]]
        description: str
        offeringType: Literal[OfferingType.CSPM_MONITOR_GIT_LAB]


    class azure.mgmt.security.types.CspmMonitorGithubOffering(TypedDict, total=False):
        key "description": str
        key "offeringType": Required[Literal[OfferingType.CSPM_MONITOR_GITHUB]]
        description: str
        offeringType: Literal[OfferingType.CSPM_MONITOR_GITHUB]


    class azure.mgmt.security.types.CspmMonitorJFrogOffering(TypedDict, total=False):
        key "description": str
        key "offeringType": Required[Literal[OfferingType.CSPM_MONITOR_J_FROG]]
        description: str
        offeringType: Literal[OfferingType.CSPM_MONITOR_J_FROG]


    class azure.mgmt.security.types.CustomRecommendation(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('CustomRecommendationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CustomRecommendationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.CustomRecommendationProperties(TypedDict, total=False):
        key "assessmentKey": str
        key "description": str
        key "displayName": str
        key "query": str
        key "remediationDescription": str
        key "securityIssue": Union[str, SecurityIssue]
        key "severity": Union[str, SeverityEnum]
        assessmentKey: str
        cloudProviders: list[Union[str, RecommendationSupportedClouds]]
        description: str
        displayName: str
        query: str
        remediationDescription: str
        securityIssue: Union[str, SecurityIssue]
        severity: Union[str, SeverityEnum]


    class azure.mgmt.security.types.DataExportSettingProperties(TypedDict, total=False):
        key "enabled": Required[bool]
        enabled: bool


    class azure.mgmt.security.types.DataExportSettings(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[SettingKind.DATA_EXPORT_SETTINGS]]
        key "name": str
        key "properties": ForwardRef('DataExportSettingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[SettingKind.DATA_EXPORT_SETTINGS]
        name: str
        properties: DataExportSettingProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.DefenderCspmAwsOffering(TypedDict, total=False):
        key "agentlessServerlessPosture": ForwardRef('DefenderCspmAwsOfferingAgentlessServerlessPosture', module='types')
        key "ciem": ForwardRef('DefenderCspmAwsOfferingCiem', module='types')
        key "dataSensitivityDiscovery": ForwardRef('DefenderCspmAwsOfferingDataSensitivityDiscovery', module='types')
        key "databasesDspm": ForwardRef('DefenderCspmAwsOfferingDatabasesDspm', module='types')
        key "description": str
        key "mdcContainersAgentlessDiscoveryK8s": ForwardRef('DefenderCspmAwsOfferingMdcContainersAgentlessDiscoveryK8S', module='types')
        key "mdcContainersImageAssessment": ForwardRef('DefenderCspmAwsOfferingMdcContainersImageAssessment', module='types')
        key "offeringType": Required[Literal[OfferingType.DEFENDER_CSPM_AWS]]
        key "serverlessContainers": ForwardRef('DefenderCspmAwsOfferingServerlessContainers', module='types')
        key "vmScanners": ForwardRef('DefenderCspmAwsOfferingVmScanners', module='types')
        agentlessServerlessPosture: DefenderCspmAwsOfferingAgentlessServerlessPosture
        ciem: DefenderCspmAwsOfferingCiem
        dataSensitivityDiscovery: DefenderCspmAwsOfferingDataSensitivityDiscovery
        databasesDspm: DefenderCspmAwsOfferingDatabasesDspm
        description: str
        mdcContainersAgentlessDiscoveryK8s: DefenderCspmAwsOfferingMdcContainersAgentlessDiscoveryK8S
        mdcContainersImageAssessment: DefenderCspmAwsOfferingMdcContainersImageAssessment
        offeringType: Literal[OfferingType.DEFENDER_CSPM_AWS]
        serverlessContainers: DefenderCspmAwsOfferingServerlessContainers
        vmScanners: DefenderCspmAwsOfferingVmScanners


    class azure.mgmt.security.types.DefenderCspmAwsOfferingAgentlessServerlessPosture(TypedDict, total=False):
        key "cloudRoleArn": str
        key "enabled": bool
        cloudRoleArn: str
        enabled: bool


    class azure.mgmt.security.types.DefenderCspmAwsOfferingCiem(TypedDict, total=False):
        key "ciemOidc": ForwardRef('DefenderCspmAwsOfferingCiemOidc', module='types')
        key "cloudTrailAuditLogIngestion": ForwardRef('AwsCloudTrailConfiguration', module='types')
        key "logCollectionOidc": ForwardRef('DefenderCspmAwsOfferingCiemLogCollectionOidc', module='types')
        ciemOidc: DefenderCspmAwsOfferingCiemOidc
        cloudTrailAuditLogIngestion: AwsCloudTrailConfiguration
        logCollectionOidc: DefenderCspmAwsOfferingCiemLogCollectionOidc


    class azure.mgmt.security.types.DefenderCspmAwsOfferingCiemLogCollectionOidc(TypedDict, total=False):
        key "cloudRoleArn": str
        cloudRoleArn: str


    class azure.mgmt.security.types.DefenderCspmAwsOfferingCiemOidc(TypedDict, total=False):
        key "azureActiveDirectoryAppName": str
        key "cloudRoleArn": str
        azureActiveDirectoryAppName: str
        cloudRoleArn: str


    class azure.mgmt.security.types.DefenderCspmAwsOfferingDataSensitivityDiscovery(TypedDict, total=False):
        key "cloudRoleArn": str
        key "enabled": bool
        cloudRoleArn: str
        enabled: bool


    class azure.mgmt.security.types.DefenderCspmAwsOfferingDatabasesDspm(TypedDict, total=False):
        key "cloudRoleArn": str
        key "enabled": bool
        cloudRoleArn: str
        enabled: bool


    class azure.mgmt.security.types.DefenderCspmAwsOfferingMdcContainersAgentlessDiscoveryK8S(TypedDict, total=False):
        key "cloudRoleArn": str
        key "enabled": bool
        cloudRoleArn: str
        enabled: bool


    class azure.mgmt.security.types.DefenderCspmAwsOfferingMdcContainersImageAssessment(TypedDict, total=False):
        key "cloudRoleArn": str
        key "enabled": bool
        key "securityFindingsEnabled": bool
        cloudRoleArn: str
        enabled: bool
        securityFindingsEnabled: bool


    class azure.mgmt.security.types.DefenderCspmAwsOfferingServerlessContainers(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.security.types.DefenderCspmAwsOfferingVmScanners(VmScannersAws):
        key "cloudRoleArn": str
        key "configuration": ForwardRef('VmScannersBaseConfiguration', module='types')
        key "enabled": bool
        cloudRoleArn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderCspmDockerHubOffering(TypedDict, total=False):
        key "description": str
        key "offeringType": Required[Literal[OfferingType.DEFENDER_CSPM_DOCKER_HUB]]
        description: str
        offeringType: Literal[OfferingType.DEFENDER_CSPM_DOCKER_HUB]


    class azure.mgmt.security.types.DefenderCspmGcpOffering(TypedDict, total=False):
        key "ciem": ForwardRef('DefenderCspmGcpOfferingCiem', module='types')
        key "ciemDiscovery": ForwardRef('DefenderCspmGcpOfferingCiemDiscovery', module='types')
        key "dataSensitivityDiscovery": ForwardRef('DefenderCspmGcpOfferingDataSensitivityDiscovery', module='types')
        key "description": str
        key "mdcContainersAgentlessDiscoveryK8s": ForwardRef('DefenderCspmGcpOfferingMdcContainersAgentlessDiscoveryK8S', module='types')
        key "mdcContainersImageAssessment": ForwardRef('DefenderCspmGcpOfferingMdcContainersImageAssessment', module='types')
        key "offeringType": Required[Literal[OfferingType.DEFENDER_CSPM_GCP]]
        key "vmScanners": ForwardRef('DefenderCspmGcpOfferingVmScanners', module='types')
        ciem: DefenderCspmGcpOfferingCiem
        ciemDiscovery: DefenderCspmGcpOfferingCiemDiscovery
        dataSensitivityDiscovery: DefenderCspmGcpOfferingDataSensitivityDiscovery
        description: str
        mdcContainersAgentlessDiscoveryK8s: DefenderCspmGcpOfferingMdcContainersAgentlessDiscoveryK8S
        mdcContainersImageAssessment: DefenderCspmGcpOfferingMdcContainersImageAssessment
        offeringType: Literal[OfferingType.DEFENDER_CSPM_GCP]
        vmScanners: DefenderCspmGcpOfferingVmScanners


    class azure.mgmt.security.types.DefenderCspmGcpOfferingCiem(TypedDict, total=False):
        key "ciemOidc": ForwardRef('DefenderCspmGcpOfferingCiemOidc', module='types')
        key "gcpAuditLogIngestion": ForwardRef('GcpAuditLogConfiguration', module='types')
        key "logCollectionOidc": ForwardRef('DefenderCspmGcpOfferingCiemOidc', module='types')
        ciemOidc: DefenderCspmGcpOfferingCiemOidc
        gcpAuditLogIngestion: GcpAuditLogConfiguration
        logCollectionOidc: DefenderCspmGcpOfferingCiemOidc


    class azure.mgmt.security.types.DefenderCspmGcpOfferingCiemDiscovery(TypedDict, total=False):
        key "azureActiveDirectoryAppName": str
        key "enableAuditLogIngestion": bool
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        azureActiveDirectoryAppName: str
        enableAuditLogIngestion: bool
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderCspmGcpOfferingCiemOidc(TypedDict, total=False):
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderCspmGcpOfferingDataSensitivityDiscovery(TypedDict, total=False):
        key "enabled": bool
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        enabled: bool
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderCspmGcpOfferingMdcContainersAgentlessDiscoveryK8S(TypedDict, total=False):
        key "enabled": bool
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        enabled: bool
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderCspmGcpOfferingMdcContainersImageAssessment(TypedDict, total=False):
        key "enabled": bool
        key "securityFindingsEnabled": bool
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        enabled: bool
        securityFindingsEnabled: bool
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderCspmGcpOfferingVmScanners(VmScannersGcp):
        key "configuration": ForwardRef('VmScannersBaseConfiguration', module='types')
        key "enabled": bool
        configuration: VmScannersBaseConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderCspmJFrogOffering(TypedDict, total=False):
        key "description": str
        key "mdcContainersImageAssessment": ForwardRef('DefenderCspmJFrogOfferingMdcContainersImageAssessment', module='types')
        key "offeringType": Required[Literal[OfferingType.DEFENDER_CSPM_J_FROG]]
        description: str
        mdcContainersImageAssessment: DefenderCspmJFrogOfferingMdcContainersImageAssessment
        offeringType: Literal[OfferingType.DEFENDER_CSPM_J_FROG]


    class azure.mgmt.security.types.DefenderCspmJFrogOfferingMdcContainersImageAssessment(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.security.types.DefenderFoDatabasesAwsOffering(TypedDict, total=False):
        key "arcAutoProvisioning": ForwardRef('DefenderFoDatabasesAwsOfferingArcAutoProvisioning', module='types')
        key "databasesDspm": ForwardRef('DefenderFoDatabasesAwsOfferingDatabasesDspm', module='types')
        key "description": str
        key "offeringType": Required[Literal[OfferingType.DEFENDER_FOR_DATABASES_AWS]]
        key "rds": ForwardRef('DefenderFoDatabasesAwsOfferingRds', module='types')
        arcAutoProvisioning: DefenderFoDatabasesAwsOfferingArcAutoProvisioning
        databasesDspm: DefenderFoDatabasesAwsOfferingDatabasesDspm
        description: str
        offeringType: Literal[OfferingType.DEFENDER_FOR_DATABASES_AWS]
        rds: DefenderFoDatabasesAwsOfferingRds


    class azure.mgmt.security.types.DefenderFoDatabasesAwsOfferingArcAutoProvisioning(ArcAutoProvisioningAws):
        key "cloudRoleArn": str
        key "configuration": ForwardRef('ArcAutoProvisioningConfiguration', module='types')
        key "enabled": bool
        cloudRoleArn: str
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderFoDatabasesAwsOfferingDatabasesDspm(TypedDict, total=False):
        key "cloudRoleArn": str
        key "enabled": bool
        cloudRoleArn: str
        enabled: bool


    class azure.mgmt.security.types.DefenderFoDatabasesAwsOfferingRds(TypedDict, total=False):
        key "cloudRoleArn": str
        key "enabled": bool
        cloudRoleArn: str
        enabled: bool


    class azure.mgmt.security.types.DefenderForContainersAwsOffering(TypedDict, total=False):
        key "cloudWatchToKinesis": ForwardRef('DefenderForContainersAwsOfferingCloudWatchToKinesis', module='types')
        key "containerAntiMalwareEnabled": bool
        key "dataCollectionExternalId": str
        key "description": str
        key "enableAuditLogsAutoProvisioning": bool
        key "enableDefenderAgentAutoProvisioning": bool
        key "enablePolicyAgentAutoProvisioning": bool
        key "installationMethod": Union[str, InstallationMethod]
        key "kinesisToS3": ForwardRef('DefenderForContainersAwsOfferingKinesisToS3', module='types')
        key "kubeAuditRetentionTime": int
        key "kubernetesDataCollection": ForwardRef('DefenderForContainersAwsOfferingKubernetesDataCollection', module='types')
        key "kubernetesService": ForwardRef('DefenderForContainersAwsOfferingKubernetesService', module='types')
        key "mdcContainersAgentlessDiscoveryK8s": ForwardRef('DefenderForContainersAwsOfferingMdcContainersAgentlessDiscoveryK8S', module='types')
        key "mdcContainersImageAssessment": ForwardRef('DefenderForContainersAwsOfferingMdcContainersImageAssessment', module='types')
        key "offeringType": Required[Literal[OfferingType.DEFENDER_FOR_CONTAINERS_AWS]]
        key "securityGatingEnabled": bool
        key "vmScanners": ForwardRef('DefenderForContainersAwsOfferingVmScanners', module='types')
        cloudWatchToKinesis: DefenderForContainersAwsOfferingCloudWatchToKinesis
        containerAntiMalwareEnabled: bool
        dataCollectionExternalId: str
        description: str
        enableAuditLogsAutoProvisioning: bool
        enableDefenderAgentAutoProvisioning: bool
        enablePolicyAgentAutoProvisioning: bool
        installationMethod: Union[str, InstallationMethod]
        kinesisToS3: DefenderForContainersAwsOfferingKinesisToS3
        kubeAuditRetentionTime: int
        kubernetesDataCollection: DefenderForContainersAwsOfferingKubernetesDataCollection
        kubernetesService: DefenderForContainersAwsOfferingKubernetesService
        mdcContainersAgentlessDiscoveryK8s: DefenderForContainersAwsOfferingMdcContainersAgentlessDiscoveryK8S
        mdcContainersImageAssessment: DefenderForContainersAwsOfferingMdcContainersImageAssessment
        offeringType: Literal[OfferingType.DEFENDER_FOR_CONTAINERS_AWS]
        securityGatingEnabled: bool
        vmScanners: DefenderForContainersAwsOfferingVmScanners


    class azure.mgmt.security.types.DefenderForContainersAwsOfferingCloudWatchToKinesis(TypedDict, total=False):
        key "cloudRoleArn": str
        cloudRoleArn: str


    class azure.mgmt.security.types.DefenderForContainersAwsOfferingKinesisToS3(TypedDict, total=False):
        key "cloudRoleArn": str
        cloudRoleArn: str


    class azure.mgmt.security.types.DefenderForContainersAwsOfferingKubernetesDataCollection(TypedDict, total=False):
        key "cloudRoleArn": str
        cloudRoleArn: str


    class azure.mgmt.security.types.DefenderForContainersAwsOfferingKubernetesService(TypedDict, total=False):
        key "cloudRoleArn": str
        cloudRoleArn: str


    class azure.mgmt.security.types.DefenderForContainersAwsOfferingMdcContainersAgentlessDiscoveryK8S(TypedDict, total=False):
        key "cloudRoleArn": str
        key "enabled": bool
        cloudRoleArn: str
        enabled: bool


    class azure.mgmt.security.types.DefenderForContainersAwsOfferingMdcContainersImageAssessment(TypedDict, total=False):
        key "cloudRoleArn": str
        key "enabled": bool
        key "securityFindingsEnabled": bool
        cloudRoleArn: str
        enabled: bool
        securityFindingsEnabled: bool


    class azure.mgmt.security.types.DefenderForContainersAwsOfferingVmScanners(VmScannersAws):
        key "cloudRoleArn": str
        key "configuration": ForwardRef('VmScannersBaseConfiguration', module='types')
        key "enabled": bool
        cloudRoleArn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderForContainersDockerHubOffering(TypedDict, total=False):
        key "description": str
        key "offeringType": Required[Literal[OfferingType.DEFENDER_FOR_CONTAINERS_DOCKER_HUB]]
        description: str
        offeringType: Literal[OfferingType.DEFENDER_FOR_CONTAINERS_DOCKER_HUB]


    class azure.mgmt.security.types.DefenderForContainersGcpOffering(TypedDict, total=False):
        key "containerAntiMalwareEnabled": bool
        key "dataPipelineNativeCloudConnection": ForwardRef('DefenderForContainersGcpOfferingDataPipelineNativeCloudConnection', module='types')
        key "description": str
        key "enableAuditLogsAutoProvisioning": bool
        key "enableDefenderAgentAutoProvisioning": bool
        key "enablePolicyAgentAutoProvisioning": bool
        key "installationMethod": Union[str, InstallationMethod]
        key "mdcContainersAgentlessDiscoveryK8s": ForwardRef('DefenderForContainersGcpOfferingMdcContainersAgentlessDiscoveryK8S', module='types')
        key "mdcContainersImageAssessment": ForwardRef('DefenderForContainersGcpOfferingMdcContainersImageAssessment', module='types')
        key "nativeCloudConnection": ForwardRef('DefenderForContainersGcpOfferingNativeCloudConnection', module='types')
        key "offeringType": Required[Literal[OfferingType.DEFENDER_FOR_CONTAINERS_GCP]]
        key "securityGatingEnabled": bool
        key "vmScanners": ForwardRef('DefenderForContainersGcpOfferingVmScanners', module='types')
        containerAntiMalwareEnabled: bool
        dataPipelineNativeCloudConnection: DefenderForContainersGcpOfferingDataPipelineNativeCloudConnection
        description: str
        enableAuditLogsAutoProvisioning: bool
        enableDefenderAgentAutoProvisioning: bool
        enablePolicyAgentAutoProvisioning: bool
        installationMethod: Union[str, InstallationMethod]
        mdcContainersAgentlessDiscoveryK8s: DefenderForContainersGcpOfferingMdcContainersAgentlessDiscoveryK8S
        mdcContainersImageAssessment: DefenderForContainersGcpOfferingMdcContainersImageAssessment
        nativeCloudConnection: DefenderForContainersGcpOfferingNativeCloudConnection
        offeringType: Literal[OfferingType.DEFENDER_FOR_CONTAINERS_GCP]
        securityGatingEnabled: bool
        vmScanners: DefenderForContainersGcpOfferingVmScanners


    class azure.mgmt.security.types.DefenderForContainersGcpOfferingDataPipelineNativeCloudConnection(TypedDict, total=False):
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderForContainersGcpOfferingMdcContainersAgentlessDiscoveryK8S(TypedDict, total=False):
        key "enabled": bool
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        enabled: bool
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderForContainersGcpOfferingMdcContainersImageAssessment(TypedDict, total=False):
        key "enabled": bool
        key "securityFindingsEnabled": bool
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        enabled: bool
        securityFindingsEnabled: bool
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderForContainersGcpOfferingNativeCloudConnection(TypedDict, total=False):
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderForContainersGcpOfferingVmScanners(VmScannersGcp):
        key "configuration": ForwardRef('VmScannersBaseConfiguration', module='types')
        key "enabled": bool
        configuration: VmScannersBaseConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderForContainersJFrogOffering(TypedDict, total=False):
        key "description": str
        key "offeringType": Required[Literal[OfferingType.DEFENDER_FOR_CONTAINERS_J_FROG]]
        description: str
        offeringType: Literal[OfferingType.DEFENDER_FOR_CONTAINERS_J_FROG]


    class azure.mgmt.security.types.DefenderForDatabasesGcpOffering(TypedDict, total=False):
        key "arcAutoProvisioning": ForwardRef('DefenderForDatabasesGcpOfferingArcAutoProvisioning', module='types')
        key "defenderForDatabasesArcAutoProvisioning": ForwardRef('DefenderForDatabasesGcpOfferingDefenderForDatabasesArcAutoProvisioning', module='types')
        key "description": str
        key "offeringType": Required[Literal[OfferingType.DEFENDER_FOR_DATABASES_GCP]]
        arcAutoProvisioning: DefenderForDatabasesGcpOfferingArcAutoProvisioning
        defenderForDatabasesArcAutoProvisioning: DefenderForDatabasesGcpOfferingDefenderForDatabasesArcAutoProvisioning
        description: str
        offeringType: Literal[OfferingType.DEFENDER_FOR_DATABASES_GCP]


    class azure.mgmt.security.types.DefenderForDatabasesGcpOfferingArcAutoProvisioning(ArcAutoProvisioningGcp):
        key "configuration": ForwardRef('ArcAutoProvisioningConfiguration', module='types')
        key "enabled": bool
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderForDatabasesGcpOfferingDefenderForDatabasesArcAutoProvisioning(TypedDict, total=False):
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderForServersAwsOffering(TypedDict, total=False):
        key "arcAutoProvisioning": ForwardRef('DefenderForServersAwsOfferingArcAutoProvisioning', module='types')
        key "defenderForServers": ForwardRef('DefenderForServersAwsOfferingDefenderForServers', module='types')
        key "description": str
        key "mdeAutoProvisioning": ForwardRef('DefenderForServersAwsOfferingMdeAutoProvisioning', module='types')
        key "offeringType": Required[Literal[OfferingType.DEFENDER_FOR_SERVERS_AWS]]
        key "subPlan": ForwardRef('DefenderForServersAwsOfferingSubPlan', module='types')
        key "vaAutoProvisioning": ForwardRef('DefenderForServersAwsOfferingVaAutoProvisioning', module='types')
        key "vmScanners": ForwardRef('DefenderForServersAwsOfferingVmScanners', module='types')
        arcAutoProvisioning: DefenderForServersAwsOfferingArcAutoProvisioning
        defenderForServers: DefenderForServersAwsOfferingDefenderForServers
        description: str
        mdeAutoProvisioning: DefenderForServersAwsOfferingMdeAutoProvisioning
        offeringType: Literal[OfferingType.DEFENDER_FOR_SERVERS_AWS]
        subPlan: DefenderForServersAwsOfferingSubPlan
        vaAutoProvisioning: DefenderForServersAwsOfferingVaAutoProvisioning
        vmScanners: DefenderForServersAwsOfferingVmScanners


    class azure.mgmt.security.types.DefenderForServersAwsOfferingArcAutoProvisioning(ArcAutoProvisioningAws):
        key "cloudRoleArn": str
        key "configuration": ForwardRef('ArcAutoProvisioningConfiguration', module='types')
        key "enabled": bool
        cloudRoleArn: str
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderForServersAwsOfferingDefenderForServers(TypedDict, total=False):
        key "cloudRoleArn": str
        cloudRoleArn: str


    class azure.mgmt.security.types.DefenderForServersAwsOfferingMdeAutoProvisioning(TypedDict, total=False):
        key "configuration": Any
        key "enabled": bool
        configuration: Any
        enabled: bool


    class azure.mgmt.security.types.DefenderForServersAwsOfferingSubPlan(TypedDict, total=False):
        key "type": Union[str, SubPlan]
        type: Union[str, SubPlan]


    class azure.mgmt.security.types.DefenderForServersAwsOfferingVaAutoProvisioning(TypedDict, total=False):
        key "configuration": ForwardRef('DefenderForServersAwsOfferingVaAutoProvisioningConfiguration', module='types')
        key "enabled": bool
        configuration: DefenderForServersAwsOfferingVaAutoProvisioningConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderForServersAwsOfferingVaAutoProvisioningConfiguration(TypedDict, total=False):
        key "type": Union[str, Type]
        type: Union[str, Type]


    class azure.mgmt.security.types.DefenderForServersAwsOfferingVmScanners(VmScannersAws):
        key "cloudRoleArn": str
        key "configuration": ForwardRef('VmScannersBaseConfiguration', module='types')
        key "enabled": bool
        cloudRoleArn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderForServersGcpOffering(TypedDict, total=False):
        key "arcAutoProvisioning": ForwardRef('DefenderForServersGcpOfferingArcAutoProvisioning', module='types')
        key "defenderForServers": ForwardRef('DefenderForServersGcpOfferingDefenderForServers', module='types')
        key "description": str
        key "mdeAutoProvisioning": ForwardRef('DefenderForServersGcpOfferingMdeAutoProvisioning', module='types')
        key "offeringType": Required[Literal[OfferingType.DEFENDER_FOR_SERVERS_GCP]]
        key "subPlan": ForwardRef('DefenderForServersGcpOfferingSubPlan', module='types')
        key "vaAutoProvisioning": ForwardRef('DefenderForServersGcpOfferingVaAutoProvisioning', module='types')
        key "vmScanners": ForwardRef('DefenderForServersGcpOfferingVmScanners', module='types')
        arcAutoProvisioning: DefenderForServersGcpOfferingArcAutoProvisioning
        defenderForServers: DefenderForServersGcpOfferingDefenderForServers
        description: str
        mdeAutoProvisioning: DefenderForServersGcpOfferingMdeAutoProvisioning
        offeringType: Literal[OfferingType.DEFENDER_FOR_SERVERS_GCP]
        subPlan: DefenderForServersGcpOfferingSubPlan
        vaAutoProvisioning: DefenderForServersGcpOfferingVaAutoProvisioning
        vmScanners: DefenderForServersGcpOfferingVmScanners


    class azure.mgmt.security.types.DefenderForServersGcpOfferingArcAutoProvisioning(ArcAutoProvisioningGcp):
        key "configuration": ForwardRef('ArcAutoProvisioningConfiguration', module='types')
        key "enabled": bool
        configuration: ArcAutoProvisioningConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderForServersGcpOfferingDefenderForServers(TypedDict, total=False):
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.DefenderForServersGcpOfferingMdeAutoProvisioning(TypedDict, total=False):
        key "configuration": Any
        key "enabled": bool
        configuration: Any
        enabled: bool


    class azure.mgmt.security.types.DefenderForServersGcpOfferingSubPlan(TypedDict, total=False):
        key "type": Union[str, SubPlan]
        type: Union[str, SubPlan]


    class azure.mgmt.security.types.DefenderForServersGcpOfferingVaAutoProvisioning(TypedDict, total=False):
        key "configuration": ForwardRef('DefenderForServersGcpOfferingVaAutoProvisioningConfiguration', module='types')
        key "enabled": bool
        configuration: DefenderForServersGcpOfferingVaAutoProvisioningConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderForServersGcpOfferingVaAutoProvisioningConfiguration(TypedDict, total=False):
        key "type": Union[str, Type]
        type: Union[str, Type]


    class azure.mgmt.security.types.DefenderForServersGcpOfferingVmScanners(VmScannersGcp):
        key "configuration": ForwardRef('VmScannersBaseConfiguration', module='types')
        key "enabled": bool
        configuration: VmScannersBaseConfiguration
        enabled: bool


    class azure.mgmt.security.types.DefenderForStorageSetting(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DefenderForStorageSettingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DefenderForStorageSettingProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.DefenderForStorageSettingProperties(TypedDict, total=False):
        key "isEnabled": bool
        key "malwareScanning": ForwardRef('MalwareScanningProperties', module='types')
        key "managedBy": Union[str, ManagedByType]
        key "overrideSubscriptionLevelSettings": bool
        key "sensitiveDataDiscovery": ForwardRef('SensitiveDataDiscoveryProperties', module='types')
        isEnabled: bool
        malwareScanning: MalwareScanningProperties
        managedBy: Union[str, ManagedByType]
        overrideSubscriptionLevelSettings: bool
        sensitiveDataDiscovery: SensitiveDataDiscoveryProperties


    class azure.mgmt.security.types.DenylistCustomAlertRule(TypedDict, total=False):
        key "denylistValues": Required[list[str]]
        key "description": str
        key "displayName": str
        key "isEnabled": Required[bool]
        key "ruleType": Required[Literal["DenylistCustomAlertRule"]]
        key "valueType": Union[str, ValueType]
        denylistValues: list[str]
        description: str
        displayName: str
        isEnabled: bool
        ruleType: Literal[DenylistCustomAlertRule]
        valueType: Union[str, ValueType]


    class azure.mgmt.security.types.DevOpsCapability(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.security.types.DevOpsConfiguration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DevOpsConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DevOpsConfigurationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.DevOpsConfigurationProperties(TypedDict, total=False):
        key "agentlessConfiguration": ForwardRef('AgentlessConfiguration', module='types')
        key "authorization": ForwardRef('Authorization', module='types')
        key "autoDiscovery": Union[str, AutoDiscovery]
        key "provisioningState": Union[str, DevOpsProvisioningState]
        key "provisioningStatusMessage": str
        key "provisioningStatusUpdateTimeUtc": str
        agentlessConfiguration: AgentlessConfiguration
        authorization: Authorization
        autoDiscovery: Union[str, AutoDiscovery]
        capabilities: list[DevOpsCapability]
        provisioningState: Union[str, DevOpsProvisioningState]
        provisioningStatusMessage: str
        provisioningStatusUpdateTimeUtc: str
        topLevelInventoryList: list[str]


    class azure.mgmt.security.types.DeviceSecurityGroup(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DeviceSecurityGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DeviceSecurityGroupProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.DeviceSecurityGroupProperties(TypedDict, total=False):
        allowlistRules: list[AllowlistCustomAlertRule]
        denylistRules: list[DenylistCustomAlertRule]
        thresholdRules: list[ThresholdCustomAlertRule]
        timeWindowRules: list[TimeWindowCustomAlertRule]


    class azure.mgmt.security.types.DockerHubEnvironmentData(TypedDict, total=False):
        key "authentication": ForwardRef('Authentication', module='types')
        key "environmentType": Required[Literal[EnvironmentType.DOCKER_HUB_ORGANIZATION]]
        key "scanInterval": int
        authentication: Authentication
        environmentType: Literal[EnvironmentType.DOCKER_HUB_ORGANIZATION]
        scanInterval: int


    class azure.mgmt.security.types.EnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS_ACCOUNT = "AwsAccount"
        AZURE_DEV_OPS_SCOPE = "AzureDevOpsScope"
        DOCKER_HUB_ORGANIZATION = "DockerHubOrganization"
        GCP_PROJECT = "GcpProject"
        GITHUB_SCOPE = "GithubScope"
        GITLAB_SCOPE = "GitlabScope"
        J_FROG_ARTIFACTORY = "JFrogArtifactory"


    class azure.mgmt.security.types.ExecuteGovernanceRuleParams(TypedDict, total=False):
        key "override": bool
        override: bool


    class azure.mgmt.security.types.Extension(TypedDict, total=False):
        key "isEnabled": Required[Union[str, IsEnabled]]
        key "name": Required[str]
        key "operationStatus": ForwardRef('OperationStatus', module='types')
        key "securityOperatorResourceId": str
        additionalExtensionProperties: dict[str, Any]
        isEnabled: Union[str, IsEnabled]
        name: str
        operationStatus: OperationStatus
        securityOperatorResourceId: str


    class azure.mgmt.security.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.FileScanFilter(TypedDict, total=False):
        key "file": ForwardRef('MatchFilter', module='types')
        key "share": ForwardRef('MatchFilter', module='types')
        file: MatchFilter
        share: MatchFilter


    class azure.mgmt.security.types.GcpAuditLogConfiguration(TypedDict, total=False):
        key "provisioningType": Union[str, GcpLoggingProvisioningType]
        key "resourceNamePrefix": str
        provisioningType: Union[str, GcpLoggingProvisioningType]
        resourceNamePrefix: str
        resourceSets: list[GcpLoggingResourceSet]


    class azure.mgmt.security.types.GcpLoggingResourceSet(TypedDict, total=False):
        key "pubSubSubscriptionName": str
        pubSubSubscriptionName: str


    class azure.mgmt.security.types.GcpOrganizationalDataMember(TypedDict, total=False):
        key "managementProjectNumber": str
        key "organizationMembershipType": Required[Literal[OrganizationMembershipType.MEMBER]]
        key "parentHierarchyId": str
        managementProjectNumber: str
        organizationMembershipType: Literal[OrganizationMembershipType.MEMBER]
        parentHierarchyId: str


    class azure.mgmt.security.types.GcpOrganizationalDataOrganization(TypedDict, total=False):
        key "organizationMembershipType": Required[Literal[OrganizationMembershipType.ORGANIZATION]]
        key "organizationName": str
        key "serviceAccountEmailAddress": str
        key "workloadIdentityProviderId": str
        excludedProjectNumbers: list[str]
        organizationMembershipType: Literal[OrganizationMembershipType.ORGANIZATION]
        organizationName: str
        serviceAccountEmailAddress: str
        workloadIdentityProviderId: str


    class azure.mgmt.security.types.GcpProjectDetails(TypedDict, total=False):
        key "projectId": str
        key "projectName": str
        key "projectNumber": str
        key "workloadIdentityPoolId": str
        projectId: str
        projectName: str
        projectNumber: str
        workloadIdentityPoolId: str


    class azure.mgmt.security.types.GcpProjectEnvironmentData(TypedDict, total=False):
        key "environmentType": Required[Literal[EnvironmentType.GCP_PROJECT]]
        key "organizationalData": ForwardRef('GcpOrganizationalData', module='types')
        key "projectDetails": ForwardRef('GcpProjectDetails', module='types')
        key "scanInterval": int
        environmentType: Literal[EnvironmentType.GCP_PROJECT]
        organizationalData: GcpOrganizationalData
        projectDetails: GcpProjectDetails
        scanInterval: int


    class azure.mgmt.security.types.GithubScopeEnvironmentData(TypedDict, total=False):
        key "environmentType": Required[Literal[EnvironmentType.GITHUB_SCOPE]]
        environmentType: Literal[EnvironmentType.GITHUB_SCOPE]


    class azure.mgmt.security.types.GitlabScopeEnvironmentData(TypedDict, total=False):
        key "environmentType": Required[Literal[EnvironmentType.GITLAB_SCOPE]]
        environmentType: Literal[EnvironmentType.GITLAB_SCOPE]


    class azure.mgmt.security.types.GovernanceAssignment(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GovernanceAssignmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GovernanceAssignmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.GovernanceAssignmentAdditionalData(TypedDict, total=False):
        key "ticketLink": str
        key "ticketNumber": int
        key "ticketStatus": str
        ticketLink: str
        ticketNumber: int
        ticketStatus: str


    class azure.mgmt.security.types.GovernanceAssignmentProperties(TypedDict, total=False):
        key "additionalData": ForwardRef('GovernanceAssignmentAdditionalData', module='types')
        key "governanceEmailNotification": ForwardRef('GovernanceEmailNotification', module='types')
        key "isGracePeriod": bool
        key "owner": str
        key "remediationDueDate": Required[str]
        key "remediationEta": ForwardRef('RemediationEta', module='types')
        additionalData: GovernanceAssignmentAdditionalData
        governanceEmailNotification: GovernanceEmailNotification
        isGracePeriod: bool
        owner: str
        remediationDueDate: str
        remediationEta: RemediationEta


    class azure.mgmt.security.types.GovernanceEmailNotification(TypedDict, total=False):
        key "disableManagerEmailNotification": bool
        key "disableOwnerEmailNotification": bool
        disableManagerEmailNotification: bool
        disableOwnerEmailNotification: bool


    class azure.mgmt.security.types.GovernanceRule(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GovernanceRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GovernanceRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.GovernanceRuleEmailNotification(TypedDict, total=False):
        key "disableManagerEmailNotification": bool
        key "disableOwnerEmailNotification": bool
        disableManagerEmailNotification: bool
        disableOwnerEmailNotification: bool


    class azure.mgmt.security.types.GovernanceRuleMetadata(TypedDict, total=False):
        key "createdBy": str
        key "createdOn": str
        key "updatedBy": str
        key "updatedOn": str
        createdBy: str
        createdOn: str
        updatedBy: str
        updatedOn: str


    class azure.mgmt.security.types.GovernanceRuleOwnerSource(TypedDict, total=False):
        key "type": Union[str, GovernanceRuleOwnerSourceType]
        key "value": str
        type: Union[str, GovernanceRuleOwnerSourceType]
        value: str


    class azure.mgmt.security.types.GovernanceRuleProperties(TypedDict, total=False):
        key "conditionSets": Required[list[Any]]
        key "description": str
        key "displayName": Required[str]
        key "governanceEmailNotification": ForwardRef('GovernanceRuleEmailNotification', module='types')
        key "includeMemberScopes": bool
        key "isDisabled": bool
        key "isGracePeriod": bool
        key "metadata": ForwardRef('GovernanceRuleMetadata', module='types')
        key "ownerSource": Required[GovernanceRuleOwnerSource]
        key "remediationTimeframe": str
        key "rulePriority": Required[int]
        key "ruleType": Required[Union[str, GovernanceRuleType]]
        key "sourceResourceType": Required[Union[str, GovernanceRuleSourceResourceType]]
        key "tenantId": str
        conditionSets: list[Any]
        description: str
        displayName: str
        excludedScopes: list[str]
        governanceEmailNotification: GovernanceRuleEmailNotification
        includeMemberScopes: bool
        isDisabled: bool
        isGracePeriod: bool
        metadata: GovernanceRuleMetadata
        ownerSource: GovernanceRuleOwnerSource
        remediationTimeframe: str
        rulePriority: int
        ruleType: Union[str, GovernanceRuleType]
        sourceResourceType: Union[str, GovernanceRuleSourceResourceType]
        tenantId: str


    class azure.mgmt.security.types.InformationProtectionKeyword(TypedDict, total=False):
        key "canBeNumeric": bool
        key "custom": bool
        key "excluded": bool
        key "pattern": str
        canBeNumeric: bool
        custom: bool
        excluded: bool
        pattern: str


    class azure.mgmt.security.types.InformationProtectionPolicy(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('InformationProtectionPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: InformationProtectionPolicyProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.InformationProtectionPolicyProperties(TypedDict, total=False):
        key "lastModifiedUtc": str
        key "version": str
        informationTypes: dict[str, InformationType]
        labels: dict[str, SensitivityLabel]
        lastModifiedUtc: str
        version: str


    class azure.mgmt.security.types.InformationType(TypedDict, total=False):
        key "custom": bool
        key "description": str
        key "displayName": str
        key "enabled": bool
        key "order": int
        key "recommendedLabelId": str
        custom: bool
        description: str
        displayName: str
        enabled: bool
        keywords: list[InformationProtectionKeyword]
        order: int
        recommendedLabelId: str


    class azure.mgmt.security.types.InventoryList(TypedDict, total=False):
        key "inventoryKind": Union[str, InventoryKind]
        key "value": str
        inventoryKind: Union[str, InventoryKind]
        value: str


    class azure.mgmt.security.types.IoTSecuritySolutionModel(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('IoTSecuritySolutionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: IoTSecuritySolutionProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.security.types.IoTSecuritySolutionProperties(TypedDict, total=False):
        key "displayName": Required[str]
        key "iotHubs": Required[list[str]]
        key "status": Union[str, SecuritySolutionStatus]
        key "unmaskedIpLoggingStatus": Union[str, UnmaskedIpLoggingStatus]
        key "userDefinedResources": ForwardRef('UserDefinedResourcesProperties', module='types')
        key "workspace": str
        additionalWorkspaces: list[AdditionalWorkspacesProperties]
        autoDiscoveredResources: list[str]
        disabledDataSources: list[Union[str, DataSource]]
        displayName: str
        export: list[Union[str, ExportData]]
        iotHubs: list[str]
        recommendationsConfiguration: list[RecommendationConfigurationProperties]
        status: Union[str, SecuritySolutionStatus]
        unmaskedIpLoggingStatus: Union[str, UnmaskedIpLoggingStatus]
        userDefinedResources: UserDefinedResourcesProperties
        workspace: str


    class azure.mgmt.security.types.IssueCreationRequest(TypedDict, total=False):
        key "securityAssessmentResourceId": str
        securityAssessmentResourceId: str


    class azure.mgmt.security.types.JFrogEnvironmentData(TypedDict, total=False):
        key "environmentType": Required[Literal[EnvironmentType.J_FROG_ARTIFACTORY]]
        key "scanInterval": int
        environmentType: Literal[EnvironmentType.J_FROG_ARTIFACTORY]
        scanInterval: int


    class azure.mgmt.security.types.JitNetworkAccessPolicy(ProxyResource):
        key "id": str
        key "kind": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[JitNetworkAccessPolicyProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: str
        location: str
        name: str
        properties: JitNetworkAccessPolicyProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.JitNetworkAccessPolicyInitiatePort(TypedDict, total=False):
        key "allowedSourceAddressPrefix": str
        key "endTimeUtc": Required[str]
        key "number": Required[int]
        allowedSourceAddressPrefix: str
        endTimeUtc: str
        number: int


    class azure.mgmt.security.types.JitNetworkAccessPolicyInitiateRequest(TypedDict, total=False):
        key "justification": str
        key "virtualMachines": Required[list[JitNetworkAccessPolicyInitiateVirtualMachine]]
        justification: str
        virtualMachines: list[JitNetworkAccessPolicyInitiateVirtualMachine]


    class azure.mgmt.security.types.JitNetworkAccessPolicyInitiateVirtualMachine(TypedDict, total=False):
        key "id": Required[str]
        key "ports": Required[list[JitNetworkAccessPolicyInitiatePort]]
        id: str
        ports: list[JitNetworkAccessPolicyInitiatePort]


    class azure.mgmt.security.types.JitNetworkAccessPolicyProperties(TypedDict, total=False):
        key "provisioningState": str
        key "virtualMachines": Required[list[JitNetworkAccessPolicyVirtualMachine]]
        provisioningState: str
        requests: list[JitNetworkAccessRequest]
        virtualMachines: list[JitNetworkAccessPolicyVirtualMachine]


    class azure.mgmt.security.types.JitNetworkAccessPolicyVirtualMachine(TypedDict, total=False):
        key "id": Required[str]
        key "ports": Required[list[JitNetworkAccessPortRule]]
        key "publicIpAddress": str
        id: str
        ports: list[JitNetworkAccessPortRule]
        publicIpAddress: str


    class azure.mgmt.security.types.JitNetworkAccessPortRule(TypedDict, total=False):
        key "allowedSourceAddressPrefix": str
        key "maxRequestAccessDuration": Required[str]
        key "number": Required[int]
        key "protocol": Required[Union[str, ProtocolEnum]]
        allowedSourceAddressPrefix: str
        allowedSourceAddressPrefixes: list[str]
        maxRequestAccessDuration: str
        number: int
        protocol: Union[str, ProtocolEnum]


    class azure.mgmt.security.types.JitNetworkAccessRequest(TypedDict, total=False):
        key "justification": str
        key "requestor": Required[str]
        key "startTimeUtc": Required[str]
        key "virtualMachines": Required[list[JitNetworkAccessRequestVirtualMachine]]
        justification: str
        requestor: str
        startTimeUtc: str
        virtualMachines: list[JitNetworkAccessRequestVirtualMachine]


    class azure.mgmt.security.types.JitNetworkAccessRequestPort(TypedDict, total=False):
        key "allowedSourceAddressPrefix": str
        key "endTimeUtc": Required[str]
        key "mappedPort": int
        key "number": Required[int]
        key "status": Required[Union[str, Status]]
        key "statusReason": Required[Union[str, StatusReason]]
        allowedSourceAddressPrefix: str
        allowedSourceAddressPrefixes: list[str]
        endTimeUtc: str
        mappedPort: int
        number: int
        status: Union[str, Status]
        statusReason: Union[str, StatusReason]


    class azure.mgmt.security.types.JitNetworkAccessRequestVirtualMachine(TypedDict, total=False):
        key "id": Required[str]
        key "ports": Required[list[JitNetworkAccessRequestPort]]
        id: str
        ports: list[JitNetworkAccessRequestPort]


    class azure.mgmt.security.types.KindEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUNDLES = "Bundles"


    class azure.mgmt.security.types.MalwareScanFilters(TypedDict, total=False):
        key "blobs": ForwardRef('BlobScanFilter', module='types')
        key "files": ForwardRef('FileScanFilter', module='types')
        blobs: BlobScanFilter
        files: FileScanFilter


    class azure.mgmt.security.types.MalwareScanningProperties(TypedDict, total=False):
        key "automatedResponse": Union[str, AutomatedResponseType]
        key "blobScanResultsOptions": Union[str, BlobScanResultsOptions]
        key "onUpload": ForwardRef('OnUploadProperties', module='types')
        key "operationStatus": ForwardRef('OperationStatus', module='types')
        key "scanResultsEventGridTopicResourceId": str
        key "scannerResourceId": Optional[str]
        automatedResponse: Union[str, AutomatedResponseType]
        blobScanResultsOptions: Union[str, BlobScanResultsOptions]
        onUpload: OnUploadProperties
        operationStatus: OperationStatus
        scanResultsEventGridTopicResourceId: str
        scannerResourceId: str


    class azure.mgmt.security.types.MatchFilter(TypedDict, total=False):
        key "match": Required[Union[str, MatchType]]
        key "value": Required[str]
        match: Union[str, MatchType]
        value: str


    class azure.mgmt.security.types.NotificationsSourceAlert(TypedDict, total=False):
        key "minimalSeverity": Union[str, MinimalSeverity]
        key "sourceType": Required[Literal[SourceType.ALERT]]
        minimalSeverity: Union[str, MinimalSeverity]
        sourceType: Literal[SourceType.ALERT]


    class azure.mgmt.security.types.NotificationsSourceAttackPath(TypedDict, total=False):
        key "minimalRiskLevel": Union[str, MinimalRiskLevel]
        key "sourceType": Required[Literal[SourceType.ATTACK_PATH]]
        minimalRiskLevel: Union[str, MinimalRiskLevel]
        sourceType: Literal[SourceType.ATTACK_PATH]


    class azure.mgmt.security.types.OfferingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.mgmt.security.types.OnPremiseResourceDetails(TypedDict, total=False):
        key "databaseName": Required[str]
        key "machineName": Required[str]
        key "serverName": Required[str]
        key "source": Required[Literal[Source.ON_PREMISE_SQL]]
        key "sourceComputerId": Required[str]
        key "vmuuid": Required[str]
        key "workspaceId": Required[str]
        databaseName: str
        machineName: str
        serverName: str
        source: Literal[Source.ON_PREMISE_SQL]
        sourceComputerId: str
        vmuuid: str
        workspaceId: str


    class azure.mgmt.security.types.OnPremiseSqlResourceDetails(TypedDict, total=False):
        key "databaseName": Required[str]
        key "machineName": Required[str]
        key "serverName": Required[str]
        key "source": Required[Literal[Source.ON_PREMISE_SQL]]
        key "sourceComputerId": Required[str]
        key "vmuuid": Required[str]
        key "workspaceId": Required[str]
        databaseName: str
        machineName: str
        serverName: str
        source: Literal[Source.ON_PREMISE_SQL]
        sourceComputerId: str
        vmuuid: str
        workspaceId: str


    class azure.mgmt.security.types.OnUploadFilters(TypedDict, total=False):
        key "excludeBlobsLargerThan": Optional[int]
        key "excludeBlobsWithPrefix": Optional[list[str]]
        key "excludeBlobsWithSuffix": Optional[list[str]]
        excludeBlobsLargerThan: int
        excludeBlobsWithPrefix: list[str]
        excludeBlobsWithSuffix: list[str]


    class azure.mgmt.security.types.OnUploadProperties(TypedDict, total=False):
        key "capGBPerMonth": int
        key "filters": Optional[OnUploadFilters]
        key "isEnabled": bool
        capGBPerMonth: int
        filters: OnUploadFilters
        isEnabled: bool


    class azure.mgmt.security.types.OperationStatus(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.security.types.OrganizationMembershipType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEMBER = "Member"
        ORGANIZATION = "Organization"


    class azure.mgmt.security.types.PartialAssessmentProperties(TypedDict, total=False):
        key "assessmentKey": str
        assessmentKey: str


    class azure.mgmt.security.types.Pricing(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PricingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PricingProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.PricingBatch(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PricingBatchProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PricingBatchProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.PricingBatchPlanItem(TypedDict, total=False):
        key "operationStatus": ForwardRef('PricingPlanOperationStatus', module='types')
        key "planName": Required[str]
        key "properties": Required[PricingPropertiesReference]
        operationStatus: PricingPlanOperationStatus
        planName: str
        properties: PricingPropertiesReference


    class azure.mgmt.security.types.PricingBatchProperties(TypedDict, total=False):
        key "plansConfigurations": Required[list[PricingBatchPlanItem]]
        plansConfigurations: list[PricingBatchPlanItem]


    class azure.mgmt.security.types.PricingPlanOperationStatus(TypedDict, total=False):
        key "code": Union[str, PricingPlanOperationStatusCode]
        key "message": str
        code: Union[str, PricingPlanOperationStatusCode]
        message: str


    class azure.mgmt.security.types.PricingProperties(TypedDict, total=False):
        key "deprecated": bool
        key "enablementTime": str
        key "enforce": Union[str, Enforce]
        key "freeTrialRemainingTime": str
        key "inherited": Union[str, Inherited]
        key "inheritedFrom": str
        key "managedBy": str
        key "originatedFrom": Union[str, OriginatedFrom]
        key "pricingTier": Required[Union[str, PricingTier]]
        key "resourcesCoverageStatus": Union[str, ResourcesCoverageStatus]
        key "securityOperatorResourceId": str
        key "subPlan": str
        deprecated: bool
        enablementTime: str
        enforce: Union[str, Enforce]
        extensions: list[Extension]
        freeTrialRemainingTime: str
        inherited: Union[str, Inherited]
        inheritedFrom: str
        managedBy: str
        originatedFrom: Union[str, OriginatedFrom]
        pricingTier: Union[str, PricingTier]
        replacedBy: list[str]
        resourcesCoverageStatus: Union[str, ResourcesCoverageStatus]
        securityOperatorResourceId: str
        subPlan: str


    class azure.mgmt.security.types.PricingPropertiesReference(TypedDict, total=False):


    class azure.mgmt.security.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.security.types.PrivateEndpointConnection(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.security.types.PrivateLinkGroupResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateLinkResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.PrivateLinkProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        privateEndpointConnections: list[PrivateEndpointConnection]
        privateLinkResources: list[PrivateLinkGroupResource]
        provisioningState: Union[str, ProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]


    class azure.mgmt.security.types.PrivateLinkResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[PrivateLinkProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PrivateLinkProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.security.types.PrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        groupId: str
        requiredMembers: list[str]
        requiredZoneNames: list[str]


    class azure.mgmt.security.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.security.types.PrivateLinkUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.security.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.RecommendationConfigurationProperties(TypedDict, total=False):
        key "name": str
        key "recommendationType": Required[Union[str, RecommendationType]]
        key "status": Required[Union[str, RecommendationConfigStatus]]
        name: str
        recommendationType: Union[str, RecommendationType]
        status: Union[str, RecommendationConfigStatus]


    class azure.mgmt.security.types.RemediationEta(TypedDict, total=False):
        key "eta": Required[str]
        key "justification": Required[str]
        eta: str
        justification: str


    class azure.mgmt.security.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.RuleResultsInput(TypedDict, total=False):
        key "latestScan": bool
        latestScan: bool
        results: list[list[str]]


    class azure.mgmt.security.types.RulesResultsInput(TypedDict, total=False):
        key "latestScan": bool
        latestScan: bool
        results: dict[str, list[list[str]]]


    class azure.mgmt.security.types.ScopeElement(TypedDict, total=False):
        key "field": str
        field: str


    class azure.mgmt.security.types.SecurityAssessment(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SecurityAssessmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SecurityAssessmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.SecurityAssessmentMetadataPartnerData(TypedDict, total=False):
        key "partnerName": Required[str]
        key "productName": str
        key "secret": Required[str]
        partnerName: str
        productName: str
        secret: str


    class azure.mgmt.security.types.SecurityAssessmentMetadataProperties(TypedDict, total=False):
        key "assessmentType": Required[Union[str, AssessmentType]]
        key "description": str
        key "displayName": Required[str]
        key "implementationEffort": Union[str, ImplementationEffort]
        key "partnerData": ForwardRef('SecurityAssessmentMetadataPartnerData', module='types')
        key "policyDefinitionId": str
        key "preview": bool
        key "remediationDescription": str
        key "severity": Required[Union[str, Severity]]
        key "userImpact": Union[str, UserImpact]
        assessmentType: Union[str, AssessmentType]
        categories: list[Union[str, Categories]]
        description: str
        displayName: str
        implementationEffort: Union[str, ImplementationEffort]
        partnerData: SecurityAssessmentMetadataPartnerData
        policyDefinitionId: str
        preview: bool
        remediationDescription: str
        severity: Union[str, Severity]
        threats: list[Union[str, Threats]]
        userImpact: Union[str, UserImpact]


    class azure.mgmt.security.types.SecurityAssessmentMetadataPropertiesResponse(SecurityAssessmentMetadataProperties):
        key "assessmentType": Required[Union[str, AssessmentType]]
        key "description": str
        key "displayName": Required[str]
        key "implementationEffort": Union[str, ImplementationEffort]
        key "partnerData": ForwardRef('SecurityAssessmentMetadataPartnerData', module='types')
        key "plannedDeprecationDate": str
        key "policyDefinitionId": str
        key "preview": bool
        key "publishDates": ForwardRef('SecurityAssessmentMetadataPropertiesResponsePublishDates', module='types')
        key "remediationDescription": str
        key "severity": Required[Union[str, Severity]]
        key "userImpact": Union[str, UserImpact]
        assessmentType: Union[str, AssessmentType]
        categories: list[Union[str, Categories]]
        description: str
        displayName: str
        implementationEffort: Union[str, ImplementationEffort]
        partnerData: SecurityAssessmentMetadataPartnerData
        plannedDeprecationDate: str
        policyDefinitionId: str
        preview: bool
        publishDates: SecurityAssessmentMetadataPropertiesResponsePublishDates
        remediationDescription: str
        severity: Union[str, Severity]
        tactics: list[Union[str, Tactics]]
        techniques: list[Union[str, Techniques]]
        threats: list[Union[str, Threats]]
        userImpact: Union[str, UserImpact]


    class azure.mgmt.security.types.SecurityAssessmentMetadataPropertiesResponsePublishDates(TypedDict, total=False):
        key "GA": str
        key "public": Required[str]
        GA: str
        public: str


    class azure.mgmt.security.types.SecurityAssessmentMetadataResponse(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SecurityAssessmentMetadataPropertiesResponse', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SecurityAssessmentMetadataPropertiesResponse
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.SecurityAssessmentPartnerData(TypedDict, total=False):
        key "partnerName": Required[str]
        key "secret": Required[str]
        partnerName: str
        secret: str


    class azure.mgmt.security.types.SecurityAssessmentProperties(SecurityAssessmentPropertiesBase):
        key "displayName": str
        key "links": ForwardRef('AssessmentLinks', module='types')
        key "metadata": ForwardRef('SecurityAssessmentMetadataProperties', module='types')
        key "partnersData": ForwardRef('SecurityAssessmentPartnerData', module='types')
        key "resourceDetails": Required[CommonResourceDetails]
        key "risk": ForwardRef('SecurityAssessmentPropertiesBaseRisk', module='types')
        key "status": Required[AssessmentStatus]
        additionalData: dict[str, str]
        displayName: str
        links: AssessmentLinks
        metadata: SecurityAssessmentMetadataProperties
        partnersData: SecurityAssessmentPartnerData
        resourceDetails: CommonResourceDetails
        risk: SecurityAssessmentPropertiesBaseRisk
        status: AssessmentStatus


    class azure.mgmt.security.types.SecurityAssessmentPropertiesBase(TypedDict, total=False):
        key "displayName": str
        key "links": ForwardRef('AssessmentLinks', module='types')
        key "metadata": ForwardRef('SecurityAssessmentMetadataProperties', module='types')
        key "partnersData": ForwardRef('SecurityAssessmentPartnerData', module='types')
        key "resourceDetails": Required[CommonResourceDetails]
        key "risk": ForwardRef('SecurityAssessmentPropertiesBaseRisk', module='types')
        additionalData: dict[str, str]
        displayName: str
        links: AssessmentLinks
        metadata: SecurityAssessmentMetadataProperties
        partnersData: SecurityAssessmentPartnerData
        resourceDetails: CommonResourceDetails
        risk: SecurityAssessmentPropertiesBaseRisk


    class azure.mgmt.security.types.SecurityAssessmentPropertiesBaseRisk(TypedDict, total=False):
        key "isContextualRisk": bool
        key "level": Union[str, RiskLevel]
        attackPathsReferences: list[str]
        isContextualRisk: bool
        level: Union[str, RiskLevel]
        paths: list[SecurityAssessmentPropertiesBaseRiskPathsItem]
        riskFactors: list[str]


    class azure.mgmt.security.types.SecurityAssessmentPropertiesBaseRiskPathsItem(TypedDict, total=False):
        key "id": str
        edges: list[SecurityAssessmentPropertiesBaseRiskPathsItemEdgeItem]
        id: str
        nodes: list[SecurityAssessmentPropertiesBaseRiskPathsItemNodesItem]


    class azure.mgmt.security.types.SecurityAssessmentPropertiesBaseRiskPathsItemEdgeItem(TypedDict, total=False):
        key "id": Required[str]
        key "sourceId": Required[str]
        key "targetId": Required[str]
        id: str
        sourceId: str
        targetId: str


    class azure.mgmt.security.types.SecurityAssessmentPropertiesBaseRiskPathsItemNodesItem(TypedDict, total=False):
        key "id": str
        id: str
        nodePropertiesLabel: list[str]


    class azure.mgmt.security.types.SecurityConnector(ProxyResource):
        key "etag": str
        key "id": str
        key "kind": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('SecurityConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: str
        location: str
        name: str
        properties: SecurityConnectorProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.security.types.SecurityConnectorProperties(TypedDict, total=False):
        key "environmentData": ForwardRef('EnvironmentData', module='types')
        key "environmentName": Union[str, CloudName]
        key "hierarchyIdentifier": str
        key "hierarchyIdentifierTrialEndDate": str
        environmentData: EnvironmentData
        environmentName: Union[str, CloudName]
        hierarchyIdentifier: str
        hierarchyIdentifierTrialEndDate: str
        offerings: list[CloudOffering]


    class azure.mgmt.security.types.SecurityContact(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SecurityContactProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SecurityContactProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.SecurityContactProperties(TypedDict, total=False):
        key "emails": str
        key "isEnabled": bool
        key "notificationsByRole": ForwardRef('SecurityContactPropertiesNotificationsByRole', module='types')
        key "phone": str
        emails: str
        isEnabled: bool
        notificationsByRole: SecurityContactPropertiesNotificationsByRole
        notificationsSources: list[NotificationsSource]
        phone: str


    class azure.mgmt.security.types.SecurityContactPropertiesNotificationsByRole(TypedDict, total=False):
        key "state": Union[str, State]
        roles: list[Union[str, SecurityContactRole]]
        state: Union[str, State]


    class azure.mgmt.security.types.SecurityStandard(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SecurityStandardProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SecurityStandardProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.SecurityStandardProperties(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "metadata": ForwardRef('StandardMetadata', module='types')
        key "policySetDefinitionId": str
        key "standardType": Union[str, StandardType]
        assessments: list[PartialAssessmentProperties]
        cloudProviders: list[Union[str, StandardSupportedCloud]]
        description: str
        displayName: str
        metadata: StandardMetadata
        policySetDefinitionId: str
        standardType: Union[str, StandardType]


    class azure.mgmt.security.types.SensitiveDataDiscoveryProperties(TypedDict, total=False):
        key "isEnabled": bool
        key "operationStatus": ForwardRef('OperationStatus', module='types')
        key "scannerResourceId": Optional[str]
        isEnabled: bool
        operationStatus: OperationStatus
        scannerResourceId: str


    class azure.mgmt.security.types.SensitivityLabel(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "enabled": bool
        key "order": int
        key "rank": Union[str, Rank]
        description: str
        displayName: str
        enabled: bool
        order: int
        rank: Union[str, Rank]


    class azure.mgmt.security.types.ServerVulnerabilityAssessmentsAzureSettingProperties(TypedDict, total=False):
        key "selectedProvider": Required[Union[str, ServerVulnerabilityAssessmentsAzureSettingSelectedProvider]]
        selectedProvider: Union[str, ServerVulnerabilityAssessmentsAzureSettingSelectedProvider]


    class azure.mgmt.security.types.ServerVulnerabilityAssessmentsSetting(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[ServerVulnerabilityAssessmentsSettingKind.AZURE_SERVERS_SETTING]]
        key "name": str
        key "properties": ForwardRef('ServerVulnerabilityAssessmentsAzureSettingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[ServerVulnerabilityAssessmentsSettingKind.AZURE_SERVERS_SETTING]
        name: str
        properties: ServerVulnerabilityAssessmentsAzureSettingProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.ServerVulnerabilityAssessmentsSettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVERS_SETTING = "AzureServersSetting"


    class azure.mgmt.security.types.SettingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_SUPPRESSION_SETTING = "AlertSuppressionSetting"
        ALERT_SYNC_SETTINGS = "AlertSyncSettings"
        DATA_EXPORT_SETTINGS = "DataExportSettings"


    class azure.mgmt.security.types.Source(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "Aws"
        AZURE = "Azure"
        GCP = "Gcp"
        ON_PREMISE = "OnPremise"
        ON_PREMISE_RESOURCE_DETAILS = "OnPremiseResourceDetails"
        ON_PREMISE_SQL = "OnPremiseSql"


    class azure.mgmt.security.types.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT = "Alert"
        ATTACK_PATH = "AttackPath"


    class azure.mgmt.security.types.SqlVulnerabilityAssessmentSettings(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SqlVulnerabilityAssessmentSettingsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SqlVulnerabilityAssessmentSettingsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.SqlVulnerabilityAssessmentSettingsProperties(TypedDict, total=False):
        key "creationTime": str
        key "state": Union[str, SqlVulnerabilityAssessmentState]
        creationTime: str
        state: Union[str, SqlVulnerabilityAssessmentState]


    class azure.mgmt.security.types.Standard(ProxyResource):
        key "etag": str
        key "id": str
        key "kind": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('StandardProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: str
        location: str
        name: str
        properties: StandardProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.security.types.StandardAssignment(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('StandardAssignmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: StandardAssignmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.StandardAssignmentMetadata(TypedDict, total=False):
        key "createdBy": str
        key "createdOn": str
        key "lastUpdatedBy": str
        key "lastUpdatedOn": str
        createdBy: str
        createdOn: str
        lastUpdatedBy: str
        lastUpdatedOn: str


    class azure.mgmt.security.types.StandardAssignmentProperties(TypedDict, total=False):
        key "assignedStandard": ForwardRef('AssignedStandardItem', module='types')
        key "attestationData": ForwardRef('StandardAssignmentPropertiesAttestationData', module='types')
        key "description": str
        key "displayName": str
        key "effect": Union[str, Effect]
        key "exemptionData": ForwardRef('StandardAssignmentPropertiesExemptionData', module='types')
        key "expiresOn": str
        key "metadata": ForwardRef('StandardAssignmentMetadata', module='types')
        assignedStandard: AssignedStandardItem
        attestationData: StandardAssignmentPropertiesAttestationData
        description: str
        displayName: str
        effect: Union[str, Effect]
        excludedScopes: list[str]
        exemptionData: StandardAssignmentPropertiesExemptionData
        expiresOn: str
        metadata: StandardAssignmentMetadata


    class azure.mgmt.security.types.StandardAssignmentPropertiesAttestationData(TypedDict, total=False):
        key "assignedAssessment": ForwardRef('AssignedAssessmentItem', module='types')
        key "complianceDate": str
        key "complianceState": Union[str, AttestationComplianceState]
        assignedAssessment: AssignedAssessmentItem
        complianceDate: str
        complianceState: Union[str, AttestationComplianceState]
        evidence: list[AttestationEvidence]


    class azure.mgmt.security.types.StandardAssignmentPropertiesExemptionData(TypedDict, total=False):
        key "assignedAssessment": ForwardRef('AssignedAssessmentItem', module='types')
        key "exemptionCategory": Union[str, ExemptionCategory]
        assignedAssessment: AssignedAssessmentItem
        exemptionCategory: Union[str, ExemptionCategory]


    class azure.mgmt.security.types.StandardComponentProperties(TypedDict, total=False):
        key "key": str
        key: str


    class azure.mgmt.security.types.StandardMetadata(TypedDict, total=False):
        key "createdBy": str
        key "createdOn": str
        key "lastUpdatedBy": str
        key "lastUpdatedOn": str
        createdBy: str
        createdOn: str
        lastUpdatedBy: str
        lastUpdatedOn: str


    class azure.mgmt.security.types.StandardProperties(TypedDict, total=False):
        key "category": str
        key "description": str
        key "displayName": str
        key "standardType": str
        category: str
        components: list[StandardComponentProperties]
        description: str
        displayName: str
        standardType: str
        supportedClouds: list[Union[str, StandardSupportedClouds]]


    class azure.mgmt.security.types.StartMalwareScanRequest(TypedDict, total=False):
        key "properties": ForwardRef('StartMalwareScanRequestProperties', module='types')
        properties: StartMalwareScanRequestProperties


    class azure.mgmt.security.types.StartMalwareScanRequestProperties(TypedDict, total=False):
        key "filters": ForwardRef('MalwareScanFilters', module='types')
        filters: MalwareScanFilters


    class azure.mgmt.security.types.SuppressionAlertsScope(TypedDict, total=False):
        key "allOf": Required[list[ScopeElement]]
        allOf: list[ScopeElement]


    class azure.mgmt.security.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.security.types.Tags(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.security.types.TagsResource(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.security.types.TargetBranchConfiguration(TypedDict, total=False):
        key "annotateDefaultBranch": Union[str, AnnotateDefaultBranchState]
        annotateDefaultBranch: Union[str, AnnotateDefaultBranchState]
        branchNames: list[str]


    class azure.mgmt.security.types.ThresholdCustomAlertRule(TypedDict, total=False):
        key "ruleType": Required[Literal["TimeWindowCustomAlertRule"]]
        key "timeWindowSize": Required[str]
        ruleType: Literal[TimeWindowCustomAlertRule]
        timeWindowSize: str


    class azure.mgmt.security.types.TimeWindowCustomAlertRule(TypedDict, total=False):
        key "ruleType": Required[Literal["TimeWindowCustomAlertRule"]]
        key "timeWindowSize": Required[str]
        ruleType: Literal[TimeWindowCustomAlertRule]
        timeWindowSize: str


    class azure.mgmt.security.types.TrackedResource(Resource):
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


    class azure.mgmt.security.types.UpdateIoTSecuritySolutionProperties(TypedDict, total=False):
        key "userDefinedResources": ForwardRef('UserDefinedResourcesProperties', module='types')
        recommendationsConfiguration: list[RecommendationConfigurationProperties]
        userDefinedResources: UserDefinedResourcesProperties


    class azure.mgmt.security.types.UpdateIotSecuritySolutionData(TagsResource):
        key "properties": ForwardRef('UpdateIoTSecuritySolutionProperties', module='types')
        properties: UpdateIoTSecuritySolutionProperties
        tags: dict[str, str]


    class azure.mgmt.security.types.UpdateSensitivitySettingsRequest(TypedDict, total=False):
        key "sensitiveInfoTypesIds": Required[list[str]]
        key "sensitivityThresholdLabelId": str
        key "sensitivityThresholdLabelOrder": float
        sensitiveInfoTypesIds: list[str]
        sensitivityThresholdLabelId: str
        sensitivityThresholdLabelOrder: float


    class azure.mgmt.security.types.UserDefinedResourcesProperties(TypedDict, total=False):
        key "query": Required[Optional[str]]
        key "querySubscriptions": Required[Optional[list[str]]]
        query: str
        querySubscriptions: list[str]


    class azure.mgmt.security.types.VmScannersAws(VmScannersBase):
        key "cloudRoleArn": str
        key "configuration": ForwardRef('VmScannersBaseConfiguration', module='types')
        key "enabled": bool
        cloudRoleArn: str
        configuration: VmScannersBaseConfiguration
        enabled: bool


    class azure.mgmt.security.types.VmScannersBase(TypedDict, total=False):
        key "configuration": ForwardRef('VmScannersBaseConfiguration', module='types')
        key "enabled": bool
        configuration: VmScannersBaseConfiguration
        enabled: bool


    class azure.mgmt.security.types.VmScannersBaseConfiguration(TypedDict, total=False):
        key "scanningMode": Union[str, ScanningMode]
        exclusionTags: dict[str, str]
        scanningMode: Union[str, ScanningMode]


    class azure.mgmt.security.types.VmScannersGcp(VmScannersBase):
        key "configuration": ForwardRef('VmScannersBaseConfiguration', module='types')
        key "enabled": bool
        configuration: VmScannersBaseConfiguration
        enabled: bool


    class azure.mgmt.security.types.WorkspaceSetting(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('WorkspaceSettingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: WorkspaceSettingProperties
        systemData: SystemData
        type: str


    class azure.mgmt.security.types.WorkspaceSettingProperties(TypedDict, total=False):
        key "scope": Required[str]
        key "workspaceId": Required[str]
        scope: str
        workspaceId: str


```