```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.authorization

    class azure.mgmt.authorization.AuthorizationManagementClient: implements ContextManager 
        access_review_default_settings: AccessReviewDefaultSettingsOperations
        access_review_history_definition: AccessReviewHistoryDefinitionOperations
        access_review_history_definition_instance: AccessReviewHistoryDefinitionInstanceOperations
        access_review_history_definition_instances: AccessReviewHistoryDefinitionInstancesOperations
        access_review_history_definitions: AccessReviewHistoryDefinitionsOperations
        access_review_instance: AccessReviewInstanceOperations
        access_review_instance_contacted_reviewers: AccessReviewInstanceContactedReviewersOperations
        access_review_instance_decisions: AccessReviewInstanceDecisionsOperations
        access_review_instance_my_decisions: AccessReviewInstanceMyDecisionsOperations
        access_review_instances: AccessReviewInstancesOperations
        access_review_instances_assigned_for_my_approval: AccessReviewInstancesAssignedForMyApprovalOperations
        access_review_schedule_definitions: AccessReviewScheduleDefinitionsOperations
        access_review_schedule_definitions_assigned_for_my_approval: AccessReviewScheduleDefinitionsAssignedForMyApprovalOperations
        alert_configurations: AlertConfigurationsOperations
        alert_definitions: AlertDefinitionsOperations
        alert_incidents: AlertIncidentsOperations
        alert_operation: AlertOperationOperations
        alerts: AlertsOperations
        attribute_namespaces: AttributeNamespacesOperations
        classic_administrators: ClassicAdministratorsOperations
        deny_assignments: DenyAssignmentsOperations
        eligible_child_resources: EligibleChildResourcesOperations
        global_administrator: GlobalAdministratorOperations
        operations: Operations
        permissions: PermissionsOperations
        provider_operations_metadata: ProviderOperationsMetadataOperations
        role_assignment_schedule_instances: RoleAssignmentScheduleInstancesOperations
        role_assignment_schedule_requests: RoleAssignmentScheduleRequestsOperations
        role_assignment_schedules: RoleAssignmentSchedulesOperations
        role_assignments: RoleAssignmentsOperations
        role_definitions: RoleDefinitionsOperations
        role_eligibility_schedule_instances: RoleEligibilityScheduleInstancesOperations
        role_eligibility_schedule_requests: RoleEligibilityScheduleRequestsOperations
        role_eligibility_schedules: RoleEligibilitySchedulesOperations
        role_management_policies: RoleManagementPoliciesOperations
        role_management_policy_assignments: RoleManagementPolicyAssignmentsOperations
        scope_access_review_default_settings: ScopeAccessReviewDefaultSettingsOperations
        scope_access_review_history_definition: ScopeAccessReviewHistoryDefinitionOperations
        scope_access_review_history_definition_instance: ScopeAccessReviewHistoryDefinitionInstanceOperations
        scope_access_review_history_definition_instances: ScopeAccessReviewHistoryDefinitionInstancesOperations
        scope_access_review_history_definitions: ScopeAccessReviewHistoryDefinitionsOperations
        scope_access_review_instance: ScopeAccessReviewInstanceOperations
        scope_access_review_instance_contacted_reviewers: ScopeAccessReviewInstanceContactedReviewersOperations
        scope_access_review_instance_decisions: ScopeAccessReviewInstanceDecisionsOperations
        scope_access_review_instances: ScopeAccessReviewInstancesOperations
        scope_access_review_schedule_definitions: ScopeAccessReviewScheduleDefinitionsOperations
        tenant_level_access_review_instance_contacted_reviewers: TenantLevelAccessReviewInstanceContactedReviewersOperations

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


namespace azure.mgmt.authorization.aio

    class azure.mgmt.authorization.aio.AuthorizationManagementClient: implements AsyncContextManager 
        access_review_default_settings: AccessReviewDefaultSettingsOperations
        access_review_history_definition: AccessReviewHistoryDefinitionOperations
        access_review_history_definition_instance: AccessReviewHistoryDefinitionInstanceOperations
        access_review_history_definition_instances: AccessReviewHistoryDefinitionInstancesOperations
        access_review_history_definitions: AccessReviewHistoryDefinitionsOperations
        access_review_instance: AccessReviewInstanceOperations
        access_review_instance_contacted_reviewers: AccessReviewInstanceContactedReviewersOperations
        access_review_instance_decisions: AccessReviewInstanceDecisionsOperations
        access_review_instance_my_decisions: AccessReviewInstanceMyDecisionsOperations
        access_review_instances: AccessReviewInstancesOperations
        access_review_instances_assigned_for_my_approval: AccessReviewInstancesAssignedForMyApprovalOperations
        access_review_schedule_definitions: AccessReviewScheduleDefinitionsOperations
        access_review_schedule_definitions_assigned_for_my_approval: AccessReviewScheduleDefinitionsAssignedForMyApprovalOperations
        alert_configurations: AlertConfigurationsOperations
        alert_definitions: AlertDefinitionsOperations
        alert_incidents: AlertIncidentsOperations
        alert_operation: AlertOperationOperations
        alerts: AlertsOperations
        attribute_namespaces: AttributeNamespacesOperations
        classic_administrators: ClassicAdministratorsOperations
        deny_assignments: DenyAssignmentsOperations
        eligible_child_resources: EligibleChildResourcesOperations
        global_administrator: GlobalAdministratorOperations
        operations: Operations
        permissions: PermissionsOperations
        provider_operations_metadata: ProviderOperationsMetadataOperations
        role_assignment_schedule_instances: RoleAssignmentScheduleInstancesOperations
        role_assignment_schedule_requests: RoleAssignmentScheduleRequestsOperations
        role_assignment_schedules: RoleAssignmentSchedulesOperations
        role_assignments: RoleAssignmentsOperations
        role_definitions: RoleDefinitionsOperations
        role_eligibility_schedule_instances: RoleEligibilityScheduleInstancesOperations
        role_eligibility_schedule_requests: RoleEligibilityScheduleRequestsOperations
        role_eligibility_schedules: RoleEligibilitySchedulesOperations
        role_management_policies: RoleManagementPoliciesOperations
        role_management_policy_assignments: RoleManagementPolicyAssignmentsOperations
        scope_access_review_default_settings: ScopeAccessReviewDefaultSettingsOperations
        scope_access_review_history_definition: ScopeAccessReviewHistoryDefinitionOperations
        scope_access_review_history_definition_instance: ScopeAccessReviewHistoryDefinitionInstanceOperations
        scope_access_review_history_definition_instances: ScopeAccessReviewHistoryDefinitionInstancesOperations
        scope_access_review_history_definitions: ScopeAccessReviewHistoryDefinitionsOperations
        scope_access_review_instance: ScopeAccessReviewInstanceOperations
        scope_access_review_instance_contacted_reviewers: ScopeAccessReviewInstanceContactedReviewersOperations
        scope_access_review_instance_decisions: ScopeAccessReviewInstanceDecisionsOperations
        scope_access_review_instances: ScopeAccessReviewInstancesOperations
        scope_access_review_schedule_definitions: ScopeAccessReviewScheduleDefinitionsOperations
        tenant_level_access_review_instance_contacted_reviewers: TenantLevelAccessReviewInstanceContactedReviewersOperations

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


namespace azure.mgmt.authorization.aio.operations

    class azure.mgmt.authorization.aio.operations.AccessReviewDefaultSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(self, **kwargs: Any) -> AccessReviewDefaultSettings: ...

        @overload
        async def put(
                self, 
                properties: AccessReviewScheduleSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...

        @overload
        async def put(
                self, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...

        @overload
        async def put(
                self, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewHistoryDefinitionInstanceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def generate_download_uri(
                self, 
                history_definition_id: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AccessReviewHistoryInstance: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewHistoryDefinitionInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewHistoryInstance]: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewHistoryDefinitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                history_definition_id: str, 
                properties: AccessReviewHistoryDefinitionProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @overload
        async def create(
                self, 
                history_definition_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @overload
        async def create(
                self, 
                history_definition_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @distributed_trace_async
        async def delete_by_id(
                self, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewHistoryDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewHistoryDefinition]: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewInstanceContactedReviewersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewContactedReviewer]: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewInstanceDecisionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewDecision]: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewInstanceMyDecisionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                schedule_definition_id: str, 
                id: str, 
                decision_id: str, 
                **kwargs: Any
            ) -> AccessReviewDecision: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewDecision]: ...

        @overload
        async def patch(
                self, 
                schedule_definition_id: str, 
                id: str, 
                decision_id: str, 
                properties: AccessReviewDecisionProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDecision: ...

        @overload
        async def patch(
                self, 
                schedule_definition_id: str, 
                id: str, 
                decision_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDecision: ...

        @overload
        async def patch(
                self, 
                schedule_definition_id: str, 
                id: str, 
                decision_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDecision: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewInstanceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def accept_recommendations(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def apply_decisions(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def reset_decisions(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def send_reminders(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def stop(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewInstancesAssignedForMyApprovalOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewInstance]: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                schedule_definition_id: str, 
                id: str, 
                properties: AccessReviewInstanceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @overload
        async def create(
                self, 
                schedule_definition_id: str, 
                id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @overload
        async def create(
                self, 
                schedule_definition_id: str, 
                id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewInstance]: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewScheduleDefinitionsAssignedForMyApprovalOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewScheduleDefinition]: ...


    class azure.mgmt.authorization.aio.operations.AccessReviewScheduleDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update_by_id(
                self, 
                schedule_definition_id: str, 
                properties: AccessReviewScheduleDefinitionProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @overload
        async def create_or_update_by_id(
                self, 
                schedule_definition_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @overload
        async def create_or_update_by_id(
                self, 
                schedule_definition_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @distributed_trace_async
        async def delete_by_id(
                self, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewScheduleDefinition]: ...

        @distributed_trace_async
        async def stop(
                self, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.aio.operations.AlertConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                alert_id: str, 
                **kwargs: Any
            ) -> AlertConfiguration: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AlertConfiguration]: ...

        @overload
        async def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: AlertConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.aio.operations.AlertDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                alert_definition_id: str, 
                **kwargs: Any
            ) -> AlertDefinition: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AlertDefinition]: ...


    class azure.mgmt.authorization.aio.operations.AlertIncidentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                alert_id: str, 
                alert_incident_id: str, 
                **kwargs: Any
            ) -> AlertIncident: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                alert_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AlertIncident]: ...

        @distributed_trace_async
        async def remediate(
                self, 
                scope: str, 
                alert_id: str, 
                alert_incident_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.aio.operations.AlertOperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> AlertOperationResult: ...


    class azure.mgmt.authorization.aio.operations.AlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_refresh(
                self, 
                scope: str, 
                alert_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[AlertOperationResult]: ...

        @distributed_trace_async
        async def begin_refresh_all(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[AlertOperationResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                alert_id: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Alert]: ...

        @overload
        async def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: Alert, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.aio.operations.AttributeNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                attribute_namespace: str, 
                parameters: AttributeNamespaceCreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttributeNamespace: ...

        @overload
        async def create(
                self, 
                attribute_namespace: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttributeNamespace: ...

        @overload
        async def create(
                self, 
                attribute_namespace: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttributeNamespace: ...

        @distributed_trace_async
        async def delete(
                self, 
                attribute_namespace: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                attribute_namespace: str, 
                **kwargs: Any
            ) -> AttributeNamespace: ...


    class azure.mgmt.authorization.aio.operations.ClassicAdministratorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ClassicAdministrator]: ...


    class azure.mgmt.authorization.aio.operations.DenyAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                deny_assignment_id: str, 
                parameters: DenyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DenyAssignment: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                deny_assignment_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DenyAssignment: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                deny_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DenyAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                deny_assignment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                deny_assignment_id: str, 
                **kwargs: Any
            ) -> DenyAssignment: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                deny_assignment_id: str, 
                **kwargs: Any
            ) -> DenyAssignment: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DenyAssignment]: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DenyAssignment]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DenyAssignment]: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DenyAssignment]: ...


    class azure.mgmt.authorization.aio.operations.EligibleChildResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EligibleChildResource]: ...


    class azure.mgmt.authorization.aio.operations.GlobalAdministratorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def elevate_access(self, **kwargs: Any) -> None: ...


    class azure.mgmt.authorization.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.authorization.aio.operations.PermissionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Permission]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Permission]: ...


    class azure.mgmt.authorization.aio.operations.ProviderOperationsMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_provider_namespace: str, 
                *, 
                expand: str = "resourceTypes", 
                **kwargs: Any
            ) -> ProviderOperationsMetadata: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: str = "resourceTypes", 
                **kwargs: Any
            ) -> AsyncItemPaged[ProviderOperationsMetadata]: ...


    class azure.mgmt.authorization.aio.operations.RoleAssignmentScheduleInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                role_assignment_schedule_instance_name: str, 
                **kwargs: Any
            ) -> RoleAssignmentScheduleInstance: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleAssignmentScheduleInstance]: ...


    class azure.mgmt.authorization.aio.operations.RoleAssignmentScheduleRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: RoleAssignmentScheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleAssignmentScheduleRequest]: ...

        @overload
        async def validate(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: RoleAssignmentScheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @overload
        async def validate(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @overload
        async def validate(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...


    class azure.mgmt.authorization.aio.operations.RoleAssignmentSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                role_assignment_schedule_name: str, 
                **kwargs: Any
            ) -> RoleAssignmentSchedule: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleAssignmentSchedule]: ...


    class azure.mgmt.authorization.aio.operations.RoleAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_assignment_name: str, 
                parameters: RoleAssignmentCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @overload
        async def create_by_id(
                self, 
                role_assignment_id: str, 
                parameters: RoleAssignmentCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @overload
        async def create_by_id(
                self, 
                role_assignment_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @overload
        async def create_by_id(
                self, 
                role_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                role_assignment_name: str, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[RoleAssignment]: ...

        @distributed_trace_async
        async def delete_by_id(
                self, 
                role_assignment_id: str, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[RoleAssignment]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                role_assignment_name: str, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                role_assignment_id: str, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleAssignment]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleAssignment]: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleAssignment]: ...

        @distributed_trace
        def list_for_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleAssignment]: ...


    class azure.mgmt.authorization.aio.operations.RoleDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                role_definition_id: str, 
                role_definition: RoleDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleDefinition: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                role_definition_id: str, 
                role_definition: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleDefinition: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                role_definition_id: str, 
                role_definition: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleDefinition: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> Optional[RoleDefinition]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> RoleDefinition: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                role_id: str, 
                **kwargs: Any
            ) -> RoleDefinition: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleDefinition]: ...


    class azure.mgmt.authorization.aio.operations.RoleEligibilityScheduleInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                role_eligibility_schedule_instance_name: str, 
                **kwargs: Any
            ) -> RoleEligibilityScheduleInstance: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleEligibilityScheduleInstance]: ...


    class azure.mgmt.authorization.aio.operations.RoleEligibilityScheduleRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: RoleEligibilityScheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleEligibilityScheduleRequest]: ...

        @overload
        async def validate(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: RoleEligibilityScheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @overload
        async def validate(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @overload
        async def validate(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...


    class azure.mgmt.authorization.aio.operations.RoleEligibilitySchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                role_eligibility_schedule_name: str, 
                **kwargs: Any
            ) -> RoleEligibilitySchedule: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleEligibilitySchedule]: ...


    class azure.mgmt.authorization.aio.operations.RoleManagementPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                role_management_policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                role_management_policy_name: str, 
                **kwargs: Any
            ) -> RoleManagementPolicy: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleManagementPolicy]: ...

        @overload
        async def update(
                self, 
                scope: str, 
                role_management_policy_name: str, 
                parameters: RoleManagementPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicy: ...

        @overload
        async def update(
                self, 
                scope: str, 
                role_management_policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicy: ...

        @overload
        async def update(
                self, 
                scope: str, 
                role_management_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicy: ...


    class azure.mgmt.authorization.aio.operations.RoleManagementPolicyAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_management_policy_assignment_name: str, 
                parameters: RoleManagementPolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicyAssignment: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_management_policy_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicyAssignment: ...

        @overload
        async def create(
                self, 
                scope: str, 
                role_management_policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicyAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                role_management_policy_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                role_management_policy_assignment_name: str, 
                **kwargs: Any
            ) -> RoleManagementPolicyAssignment: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleManagementPolicyAssignment]: ...


    class azure.mgmt.authorization.aio.operations.ScopeAccessReviewDefaultSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...

        @overload
        async def put(
                self, 
                scope: str, 
                properties: AccessReviewScheduleSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...

        @overload
        async def put(
                self, 
                scope: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...

        @overload
        async def put(
                self, 
                scope: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...


    class azure.mgmt.authorization.aio.operations.ScopeAccessReviewHistoryDefinitionInstanceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def generate_download_uri(
                self, 
                scope: str, 
                history_definition_id: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AccessReviewHistoryInstance: ...


    class azure.mgmt.authorization.aio.operations.ScopeAccessReviewHistoryDefinitionInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewHistoryInstance]: ...


    class azure.mgmt.authorization.aio.operations.ScopeAccessReviewHistoryDefinitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                scope: str, 
                history_definition_id: str, 
                properties: AccessReviewHistoryDefinitionProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @overload
        async def create(
                self, 
                scope: str, 
                history_definition_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @overload
        async def create(
                self, 
                scope: str, 
                history_definition_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @distributed_trace_async
        async def delete_by_id(
                self, 
                scope: str, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.aio.operations.ScopeAccessReviewHistoryDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                scope: str, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewHistoryDefinition]: ...


    class azure.mgmt.authorization.aio.operations.ScopeAccessReviewInstanceContactedReviewersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewContactedReviewer]: ...


    class azure.mgmt.authorization.aio.operations.ScopeAccessReviewInstanceDecisionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewDecision]: ...


    class azure.mgmt.authorization.aio.operations.ScopeAccessReviewInstanceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def apply_decisions(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def record_all_decisions(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: RecordAllDecisionsProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def record_all_decisions(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def record_all_decisions(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def reset_decisions(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def send_reminders(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def stop(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.aio.operations.ScopeAccessReviewInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: AccessReviewInstanceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @overload
        async def create(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @overload
        async def create(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewInstance]: ...


    class azure.mgmt.authorization.aio.operations.ScopeAccessReviewScheduleDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                properties: AccessReviewScheduleDefinitionProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @overload
        async def create_or_update_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @overload
        async def create_or_update_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @distributed_trace_async
        async def delete_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewScheduleDefinition]: ...

        @distributed_trace_async
        async def stop(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.aio.operations.TenantLevelAccessReviewInstanceContactedReviewersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessReviewContactedReviewer]: ...


namespace azure.mgmt.authorization.models

    class azure.mgmt.authorization.models.AccessRecommendationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVE = "Approve"
        DENY = "Deny"
        NO_INFO_AVAILABLE = "NoInfoAvailable"


    class azure.mgmt.authorization.models.AccessReviewActorIdentity(_Model):
        principal_id: Optional[str]
        principal_name: Optional[str]
        principal_type: Optional[Union[str, AccessReviewActorIdentityType]]
        user_principal_name: Optional[str]


    class azure.mgmt.authorization.models.AccessReviewActorIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_PRINCIPAL = "servicePrincipal"
        USER = "user"


    class azure.mgmt.authorization.models.AccessReviewApplyResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLIED_SUCCESSFULLY = "AppliedSuccessfully"
        APPLIED_SUCCESSFULLY_BUT_OBJECT_NOT_FOUND = "AppliedSuccessfullyButObjectNotFound"
        APPLIED_WITH_UNKNOWN_FAILURE = "AppliedWithUnknownFailure"
        APPLYING = "Applying"
        APPLY_NOT_SUPPORTED = "ApplyNotSupported"
        NEW = "New"


    class azure.mgmt.authorization.models.AccessReviewContactedReviewer(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[AccessReviewContactedReviewerProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessReviewContactedReviewerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewContactedReviewerProperties(_Model):
        created_date_time: Optional[datetime]
        user_display_name: Optional[str]
        user_principal_name: Optional[str]


    class azure.mgmt.authorization.models.AccessReviewDecision(ProxyResource):
        id: str
        name: str
        properties: Optional[AccessReviewDecisionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessReviewDecisionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewDecisionIdentity(_Model):
        display_name: Optional[str]
        id: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewDecisionInsight(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[AccessReviewDecisionInsightProperties]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessReviewDecisionInsightProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewDecisionInsightProperties(_Model):
        insight_created_date_time: Optional[datetime]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewDecisionInsightType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USER_SIGN_IN_INSIGHT = "userSignInInsight"


    class azure.mgmt.authorization.models.AccessReviewDecisionPrincipalResourceMembership(_Model):
        membership_types: Optional[list[Union[str, AccessReviewDecisionPrincipalResourceMembershipType]]]

        @overload
        def __init__(
                self, 
                *, 
                membership_types: Optional[list[Union[str, AccessReviewDecisionPrincipalResourceMembershipType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewDecisionPrincipalResourceMembershipType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "direct"
        INDIRECT = "indirect"


    class azure.mgmt.authorization.models.AccessReviewDecisionProperties(_Model):
        applied_by: Optional[AccessReviewActorIdentity]
        applied_date_time: Optional[datetime]
        apply_result: Optional[Union[str, AccessReviewApplyResult]]
        decision: Optional[Union[str, AccessReviewResult]]
        insights: Optional[list[AccessReviewDecisionInsight]]
        justification: Optional[str]
        principal: Optional[AccessReviewDecisionIdentity]
        principal_resource_membership: Optional[AccessReviewDecisionPrincipalResourceMembership]
        recommendation: Optional[Union[str, AccessRecommendationType]]
        resource: Optional[AccessReviewDecisionResource]
        reviewed_by: Optional[AccessReviewActorIdentity]
        reviewed_date_time: Optional[datetime]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                decision: Optional[Union[str, AccessReviewResult]] = ..., 
                insights: Optional[list[AccessReviewDecisionInsight]] = ..., 
                justification: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewDecisionResource(_Model):
        display_name: Optional[str]
        id: Optional[str]
        type: Union[str, DecisionResourceType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, DecisionResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewDecisionServicePrincipalIdentity(AccessReviewDecisionIdentity, discriminator='servicePrincipal'):
        app_id: Optional[str]
        display_name: str
        id: str
        type: Literal[DecisionTargetType.SERVICE_PRINCIPAL]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewDecisionUserIdentity(AccessReviewDecisionIdentity, discriminator='user'):
        display_name: str
        id: str
        type: Literal[DecisionTargetType.USER]
        user_principal_name: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewDecisionUserSignInInsightProperties(AccessReviewDecisionInsightProperties, discriminator='userSignInInsight'):
        insight_created_date_time: datetime
        last_sign_in_date_time: Optional[datetime]
        type: Literal[AccessReviewDecisionInsightType.USER_SIGN_IN_INSIGHT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewDefaultSettings(ProxyResource):
        id: str
        name: str
        properties: Optional[AccessReviewScheduleSettings]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessReviewScheduleSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewHistoryDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[AccessReviewHistoryDefinitionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessReviewHistoryDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewHistoryDefinitionProperties(_Model):
        created_by: Optional[AccessReviewActorIdentity]
        created_date_time: Optional[datetime]
        decisions: Optional[list[Union[str, AccessReviewResult]]]
        display_name: Optional[str]
        instances: Optional[list[AccessReviewHistoryInstance]]
        review_history_period_end_date_time: Optional[datetime]
        review_history_period_start_date_time: Optional[datetime]
        scopes: Optional[list[AccessReviewScope]]
        settings: Optional[AccessReviewHistoryScheduleSettings]
        status: Optional[Union[str, AccessReviewHistoryDefinitionStatus]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                decisions: Optional[list[Union[str, AccessReviewResult]]] = ..., 
                display_name: Optional[str] = ..., 
                instances: Optional[list[AccessReviewHistoryInstance]] = ..., 
                scopes: Optional[list[AccessReviewScope]] = ..., 
                settings: Optional[AccessReviewHistoryScheduleSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewHistoryDefinitionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DONE = "Done"
        ERROR = "Error"
        IN_PROGRESS = "InProgress"
        REQUESTED = "Requested"


    class azure.mgmt.authorization.models.AccessReviewHistoryInstance(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[AccessReviewHistoryInstanceProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessReviewHistoryInstanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewHistoryInstanceProperties(_Model):
        display_name: Optional[str]
        download_uri: Optional[str]
        expiration: Optional[datetime]
        fulfilled_date_time: Optional[datetime]
        review_history_period_end_date_time: Optional[datetime]
        review_history_period_start_date_time: Optional[datetime]
        run_date_time: Optional[datetime]
        status: Optional[Union[str, AccessReviewHistoryDefinitionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                expiration: Optional[datetime] = ..., 
                fulfilled_date_time: Optional[datetime] = ..., 
                review_history_period_end_date_time: Optional[datetime] = ..., 
                review_history_period_start_date_time: Optional[datetime] = ..., 
                run_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewHistoryScheduleSettings(_Model):
        pattern: Optional[AccessReviewRecurrencePattern]
        range: Optional[AccessReviewRecurrenceRange]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                pattern: Optional[AccessReviewRecurrencePattern] = ..., 
                range: Optional[AccessReviewRecurrenceRange] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewInstance(ProxyResource):
        id: str
        name: str
        properties: Optional[AccessReviewInstanceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessReviewInstanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewInstanceProperties(_Model):
        backup_reviewers: Optional[list[AccessReviewReviewer]]
        end_date_time: Optional[datetime]
        reviewers: Optional[list[AccessReviewReviewer]]
        reviewers_type: Optional[Union[str, AccessReviewInstanceReviewersType]]
        start_date_time: Optional[datetime]
        status: Optional[Union[str, AccessReviewInstanceStatus]]

        @overload
        def __init__(
                self, 
                *, 
                backup_reviewers: Optional[list[AccessReviewReviewer]] = ..., 
                end_date_time: Optional[datetime] = ..., 
                reviewers: Optional[list[AccessReviewReviewer]] = ..., 
                start_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewInstanceReviewersType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSIGNED = "Assigned"
        MANAGERS = "Managers"
        SELF = "Self"


    class azure.mgmt.authorization.models.AccessReviewInstanceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLIED = "Applied"
        APPLYING = "Applying"
        AUTO_REVIEWED = "AutoReviewed"
        AUTO_REVIEWING = "AutoReviewing"
        COMPLETED = "Completed"
        COMPLETING = "Completing"
        INITIALIZING = "Initializing"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SCHEDULED = "Scheduled"
        STARTING = "Starting"


    class azure.mgmt.authorization.models.AccessReviewRecurrencePattern(_Model):
        interval: Optional[int]
        type: Optional[Union[str, AccessReviewRecurrencePatternType]]

        @overload
        def __init__(
                self, 
                *, 
                interval: Optional[int] = ..., 
                type: Optional[Union[str, AccessReviewRecurrencePatternType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewRecurrencePatternType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABSOLUTE_MONTHLY = "absoluteMonthly"
        WEEKLY = "weekly"


    class azure.mgmt.authorization.models.AccessReviewRecurrenceRange(_Model):
        end_date: Optional[datetime]
        number_of_occurrences: Optional[int]
        start_date: Optional[datetime]
        type: Optional[Union[str, AccessReviewRecurrenceRangeType]]

        @overload
        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                number_of_occurrences: Optional[int] = ..., 
                start_date: Optional[datetime] = ..., 
                type: Optional[Union[str, AccessReviewRecurrenceRangeType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewRecurrenceRangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        END_DATE = "endDate"
        NO_END = "noEnd"
        NUMBERED = "numbered"


    class azure.mgmt.authorization.models.AccessReviewRecurrenceSettings(_Model):
        pattern: Optional[AccessReviewRecurrencePattern]
        range: Optional[AccessReviewRecurrenceRange]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                pattern: Optional[AccessReviewRecurrencePattern] = ..., 
                range: Optional[AccessReviewRecurrenceRange] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVE = "Approve"
        DENY = "Deny"
        DONT_KNOW = "DontKnow"
        NOT_NOTIFIED = "NotNotified"
        NOT_REVIEWED = "NotReviewed"


    class azure.mgmt.authorization.models.AccessReviewReviewer(_Model):
        principal_id: Optional[str]
        principal_type: Optional[Union[str, AccessReviewReviewerType]]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewReviewerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_PRINCIPAL = "servicePrincipal"
        USER = "user"


    class azure.mgmt.authorization.models.AccessReviewScheduleDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[AccessReviewScheduleDefinitionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessReviewScheduleDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewScheduleDefinitionProperties(_Model):
        backup_reviewers: Optional[list[AccessReviewReviewer]]
        created_by: Optional[AccessReviewActorIdentity]
        description_for_admins: Optional[str]
        description_for_reviewers: Optional[str]
        display_name: Optional[str]
        instances: Optional[list[AccessReviewInstance]]
        reviewers: Optional[list[AccessReviewReviewer]]
        reviewers_type: Optional[Union[str, AccessReviewScheduleDefinitionReviewersType]]
        scope: Optional[AccessReviewScope]
        settings: Optional[AccessReviewScheduleSettings]
        status: Optional[Union[str, AccessReviewScheduleDefinitionStatus]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                backup_reviewers: Optional[list[AccessReviewReviewer]] = ..., 
                description_for_admins: Optional[str] = ..., 
                description_for_reviewers: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                instances: Optional[list[AccessReviewInstance]] = ..., 
                reviewers: Optional[list[AccessReviewReviewer]] = ..., 
                settings: Optional[AccessReviewScheduleSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewScheduleDefinitionReviewersType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSIGNED = "Assigned"
        MANAGERS = "Managers"
        SELF = "Self"


    class azure.mgmt.authorization.models.AccessReviewScheduleDefinitionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLIED = "Applied"
        APPLYING = "Applying"
        AUTO_REVIEWED = "AutoReviewed"
        AUTO_REVIEWING = "AutoReviewing"
        COMPLETED = "Completed"
        COMPLETING = "Completing"
        INITIALIZING = "Initializing"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SCHEDULED = "Scheduled"
        STARTING = "Starting"


    class azure.mgmt.authorization.models.AccessReviewScheduleSettings(_Model):
        auto_apply_decisions_enabled: Optional[bool]
        default_decision: Optional[Union[str, DefaultDecisionType]]
        default_decision_enabled: Optional[bool]
        instance_duration_in_days: Optional[int]
        justification_required_on_approval: Optional[bool]
        mail_notifications_enabled: Optional[bool]
        recommendation_look_back_duration: Optional[timedelta]
        recommendations_enabled: Optional[bool]
        recurrence: Optional[AccessReviewRecurrenceSettings]
        reminder_notifications_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                auto_apply_decisions_enabled: Optional[bool] = ..., 
                default_decision: Optional[Union[str, DefaultDecisionType]] = ..., 
                default_decision_enabled: Optional[bool] = ..., 
                instance_duration_in_days: Optional[int] = ..., 
                justification_required_on_approval: Optional[bool] = ..., 
                mail_notifications_enabled: Optional[bool] = ..., 
                recommendation_look_back_duration: Optional[timedelta] = ..., 
                recommendations_enabled: Optional[bool] = ..., 
                recurrence: Optional[AccessReviewRecurrenceSettings] = ..., 
                reminder_notifications_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewScope(_Model):
        assignment_state: Optional[Union[str, AccessReviewScopeAssignmentState]]
        exclude_resource_id: Optional[str]
        exclude_role_definition_id: Optional[str]
        expand_nested_memberships: Optional[bool]
        inactive_duration: Optional[timedelta]
        include_access_below_resource: Optional[bool]
        include_inherited_access: Optional[bool]
        principal_type: Optional[Union[str, AccessReviewScopePrincipalType]]
        resource_id: Optional[str]
        role_definition_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                exclude_resource_id: Optional[str] = ..., 
                exclude_role_definition_id: Optional[str] = ..., 
                expand_nested_memberships: Optional[bool] = ..., 
                inactive_duration: Optional[timedelta] = ..., 
                include_access_below_resource: Optional[bool] = ..., 
                include_inherited_access: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AccessReviewScopeAssignmentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        ELIGIBLE = "eligible"


    class azure.mgmt.authorization.models.AccessReviewScopePrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GUEST_USER = "guestUser"
        REDEEMED_GUEST_USER = "redeemedGuestUser"
        SERVICE_PRINCIPAL = "servicePrincipal"
        USER = "user"
        USER_GROUP = "user,group"


    class azure.mgmt.authorization.models.Alert(ExtensionResource):
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


    class azure.mgmt.authorization.models.AlertConfiguration(ExtensionResource):
        id: str
        name: str
        properties: Optional[AlertConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AlertConfigurationProperties(_Model):
        alert_configuration_type: str
        alert_definition: Optional[AlertDefinition]
        alert_definition_id: Optional[str]
        is_enabled: Optional[bool]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                alert_configuration_type: str, 
                is_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AlertDefinition(ExtensionResource):
        id: str
        name: str
        properties: Optional[AlertDefinitionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.AlertDefinitionProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        how_to_prevent: Optional[str]
        is_configurable: Optional[bool]
        is_remediatable: Optional[bool]
        mitigation_steps: Optional[str]
        scope: Optional[str]
        security_impact: Optional[str]
        severity_level: Optional[Union[str, SeverityLevel]]


    class azure.mgmt.authorization.models.AlertIncident(ExtensionResource):
        id: str
        name: str
        properties: Optional[AlertIncidentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertIncidentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AlertIncidentProperties(_Model):
        alert_incident_type: str

        @overload
        def __init__(
                self, 
                *, 
                alert_incident_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AlertOperationResult(_Model):
        created_date_time: Optional[datetime]
        id: Optional[str]
        last_action_date_time: Optional[datetime]
        resource_location: Optional[str]
        status: Optional[str]
        status_detail: Optional[str]


    class azure.mgmt.authorization.models.AlertProperties(_Model):
        alert_configuration: Optional[AlertConfiguration]
        alert_definition: Optional[AlertDefinition]
        alert_incidents: Optional[list[AlertIncident]]
        incident_count: Optional[int]
        is_active: Optional[bool]
        last_modified_date_time: Optional[datetime]
        last_scanned_date_time: Optional[datetime]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_active: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ApprovalMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_APPROVAL = "NoApproval"
        PARALLEL = "Parallel"
        SERIAL = "Serial"
        SINGLE_STAGE = "SingleStage"


    class azure.mgmt.authorization.models.ApprovalSettings(_Model):
        approval_mode: Optional[Union[str, ApprovalMode]]
        approval_stages: Optional[list[ApprovalStage]]
        is_approval_required: Optional[bool]
        is_approval_required_for_extension: Optional[bool]
        is_requestor_justification_required: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                approval_mode: Optional[Union[str, ApprovalMode]] = ..., 
                approval_stages: Optional[list[ApprovalStage]] = ..., 
                is_approval_required: Optional[bool] = ..., 
                is_approval_required_for_extension: Optional[bool] = ..., 
                is_requestor_justification_required: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ApprovalStage(_Model):
        approval_stage_time_out_in_days: Optional[int]
        escalation_approvers: Optional[list[UserSet]]
        escalation_time_in_minutes: Optional[int]
        is_approver_justification_required: Optional[bool]
        is_escalation_enabled: Optional[bool]
        primary_approvers: Optional[list[UserSet]]

        @overload
        def __init__(
                self, 
                *, 
                approval_stage_time_out_in_days: Optional[int] = ..., 
                escalation_approvers: Optional[list[UserSet]] = ..., 
                escalation_time_in_minutes: Optional[int] = ..., 
                is_approver_justification_required: Optional[bool] = ..., 
                is_escalation_enabled: Optional[bool] = ..., 
                primary_approvers: Optional[list[UserSet]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AssignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        ASSIGNED = "Assigned"


    class azure.mgmt.authorization.models.AttributeNamespace(ProxyResource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.authorization.models.AttributeNamespaceCreateRequest(_Model):
        namespace_owner_principal_id: str

        @overload
        def __init__(
                self, 
                *, 
                namespace_owner_principal_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AzureRolesAssignedOutsidePimAlertConfigurationProperties(AlertConfigurationProperties, discriminator='AzureRolesAssignedOutsidePimAlertConfiguration'):
        alert_configuration_type: Literal["AzureRolesAssignedOutsidePimAlertConfiguration"]
        alert_definition: AlertDefinition
        alert_definition_id: str
        is_enabled: bool
        scope: str

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.AzureRolesAssignedOutsidePimAlertIncidentProperties(AlertIncidentProperties, discriminator='AzureRolesAssignedOutsidePimAlertIncident'):
        alert_incident_type: Literal["AzureRolesAssignedOutsidePimAlertIncident"]
        assignee_display_name: Optional[str]
        assignee_id: Optional[str]
        assignee_user_principal_name: Optional[str]
        assignment_activated_date: Optional[datetime]
        requestor_display_name: Optional[str]
        requestor_id: Optional[str]
        requestor_user_principal_name: Optional[str]
        role_definition_id: Optional[str]
        role_display_name: Optional[str]
        role_template_id: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ClassicAdministrator(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ClassicAdministratorProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[ClassicAdministratorProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.ClassicAdministratorProperties(_Model):
        email_address: Optional[str]
        role: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email_address: Optional[str] = ..., 
                role: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.CloudErrorBody(_Model):
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


    class azure.mgmt.authorization.models.CommonUserType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "Group"
        USER = "User"


    class azure.mgmt.authorization.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.authorization.models.DecisionResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ROLE = "azureRole"


    class azure.mgmt.authorization.models.DecisionTargetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_PRINCIPAL = "servicePrincipal"
        USER = "user"


    class azure.mgmt.authorization.models.DefaultDecisionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVE = "Approve"
        DENY = "Deny"
        RECOMMENDATION = "Recommendation"


    class azure.mgmt.authorization.models.DenyAssignment(ExtensionResource):
        id: str
        name: str
        properties: Optional[DenyAssignmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DenyAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.DenyAssignmentEffect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "audit"
        ENFORCED = "enforced"


    class azure.mgmt.authorization.models.DenyAssignmentPermission(_Model):
        actions: Optional[list[str]]
        condition: Optional[str]
        condition_version: Optional[str]
        data_actions: Optional[list[str]]
        not_actions: Optional[list[str]]
        not_data_actions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[str]] = ..., 
                condition: Optional[str] = ..., 
                condition_version: Optional[str] = ..., 
                data_actions: Optional[list[str]] = ..., 
                not_actions: Optional[list[str]] = ..., 
                not_data_actions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.DenyAssignmentPrincipal(_Model):
        id: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.DenyAssignmentProperties(_Model):
        condition: Optional[str]
        condition_version: Optional[str]
        created_by: Optional[str]
        created_on: Optional[datetime]
        deny_assignment_effect: Optional[Union[str, DenyAssignmentEffect]]
        deny_assignment_name: Optional[str]
        description: Optional[str]
        do_not_apply_to_child_scopes: Optional[bool]
        exclude_principals: Optional[list[DenyAssignmentPrincipal]]
        is_system_protected: Optional[bool]
        permissions: Optional[list[DenyAssignmentPermission]]
        principals: Optional[list[DenyAssignmentPrincipal]]
        scope: Optional[str]
        updated_by: Optional[str]
        updated_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ..., 
                condition_version: Optional[str] = ..., 
                deny_assignment_effect: Optional[Union[str, DenyAssignmentEffect]] = ..., 
                deny_assignment_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                do_not_apply_to_child_scopes: Optional[bool] = ..., 
                exclude_principals: Optional[list[DenyAssignmentPrincipal]] = ..., 
                is_system_protected: Optional[bool] = ..., 
                permissions: Optional[list[DenyAssignmentPermission]] = ..., 
                principals: Optional[list[DenyAssignmentPrincipal]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.DuplicateRoleCreatedAlertConfigurationProperties(AlertConfigurationProperties, discriminator='DuplicateRoleCreatedAlertConfiguration'):
        alert_configuration_type: Literal["DuplicateRoleCreatedAlertConfiguration"]
        alert_definition: AlertDefinition
        alert_definition_id: str
        is_enabled: bool
        scope: str

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.DuplicateRoleCreatedAlertIncidentProperties(AlertIncidentProperties, discriminator='DuplicateRoleCreatedAlertIncident'):
        alert_incident_type: Literal["DuplicateRoleCreatedAlertIncident"]
        duplicate_roles: Optional[str]
        reason: Optional[str]
        role_name: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.EligibleChildResource(_Model):
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]


    class azure.mgmt.authorization.models.EnablementRules(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JUSTIFICATION = "Justification"
        MULTI_FACTOR_AUTHENTICATION = "MultiFactorAuthentication"
        TICKETING = "Ticketing"


    class azure.mgmt.authorization.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.authorization.models.ErrorDefinition(_Model):
        error: Optional[ErrorDefinitionProperties]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ErrorDefinitionProperties(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.authorization.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ExcludedPrincipalTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_PRINCIPALS_AS_REQUESTOR = "ServicePrincipalsAsRequestor"
        SERVICE_PRINCIPALS_AS_TARGET = "ServicePrincipalsAsTarget"


    class azure.mgmt.authorization.models.ExpandedProperties(_Model):
        principal: Optional[ExpandedPropertiesPrincipal]
        role_definition: Optional[ExpandedPropertiesRoleDefinition]
        scope: Optional[ExpandedPropertiesScope]

        @overload
        def __init__(
                self, 
                *, 
                principal: Optional[ExpandedPropertiesPrincipal] = ..., 
                role_definition: Optional[ExpandedPropertiesRoleDefinition] = ..., 
                scope: Optional[ExpandedPropertiesScope] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ExpandedPropertiesPrincipal(_Model):
        display_name: Optional[str]
        email: Optional[str]
        id: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                email: Optional[str] = ..., 
                id: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ExpandedPropertiesRoleDefinition(_Model):
        display_name: Optional[str]
        id: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ExpandedPropertiesScope(_Model):
        display_name: Optional[str]
        id: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.authorization.models.MemberType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        GROUP = "Group"
        INHERITED = "Inherited"


    class azure.mgmt.authorization.models.NotificationDeliveryMechanism(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMAIL = "Email"


    class azure.mgmt.authorization.models.NotificationLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        CRITICAL = "Critical"
        NONE = "None"


    class azure.mgmt.authorization.models.Operation(_Model):
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


    class azure.mgmt.authorization.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.authorization.models.PIMOnlyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        REPORT_ONLY = "ReportOnly"


    class azure.mgmt.authorization.models.PIMOnlyModeSettings(_Model):
        excluded_assignment_types: Optional[list[Union[str, ExcludedPrincipalTypes]]]
        excludes: Optional[list[UsersOrServicePrincipalSet]]
        mode: Optional[Union[str, PIMOnlyMode]]

        @overload
        def __init__(
                self, 
                *, 
                excluded_assignment_types: Optional[list[Union[str, ExcludedPrincipalTypes]]] = ..., 
                excludes: Optional[list[UsersOrServicePrincipalSet]] = ..., 
                mode: Optional[Union[str, PIMOnlyMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.Permission(_Model):
        actions: Optional[list[str]]
        condition: Optional[str]
        condition_version: Optional[str]
        data_actions: Optional[list[str]]
        not_actions: Optional[list[str]]
        not_data_actions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[str]] = ..., 
                data_actions: Optional[list[str]] = ..., 
                not_actions: Optional[list[str]] = ..., 
                not_data_actions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.PolicyAssignmentProperties(_Model):
        policy: Optional[PolicyAssignmentPropertiesPolicy]
        role_definition: Optional[PolicyAssignmentPropertiesRoleDefinition]
        scope: Optional[PolicyAssignmentPropertiesScope]

        @overload
        def __init__(
                self, 
                *, 
                policy: Optional[PolicyAssignmentPropertiesPolicy] = ..., 
                role_definition: Optional[PolicyAssignmentPropertiesRoleDefinition] = ..., 
                scope: Optional[PolicyAssignmentPropertiesScope] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.PolicyAssignmentPropertiesPolicy(_Model):
        id: Optional[str]
        last_modified_by: Optional[Principal]
        last_modified_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                last_modified_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.PolicyAssignmentPropertiesRoleDefinition(_Model):
        display_name: Optional[str]
        id: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.PolicyAssignmentPropertiesScope(_Model):
        display_name: Optional[str]
        id: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.PolicyProperties(_Model):
        scope: Optional[PolicyPropertiesScope]


    class azure.mgmt.authorization.models.PolicyPropertiesScope(_Model):
        display_name: Optional[str]
        id: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.Principal(_Model):
        display_name: Optional[str]
        email: Optional[str]
        id: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                email: Optional[str] = ..., 
                id: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.PrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVICE = "Device"
        FOREIGN_GROUP = "ForeignGroup"
        GROUP = "Group"
        SERVICE_PRINCIPAL = "ServicePrincipal"
        USER = "User"


    class azure.mgmt.authorization.models.ProviderOperation(_Model):
        description: Optional[str]
        display_name: Optional[str]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[Any]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.ProviderOperationsMetadata(SettableResource):
        display_name: Optional[str]
        id: str
        name: str
        operations: Optional[list[ProviderOperation]]
        resource_types: Optional[list[ResourceType]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[ProviderOperation]] = ..., 
                resource_types: Optional[list[ResourceType]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.authorization.models.RecipientType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN = "Admin"
        APPROVER = "Approver"
        REQUESTOR = "Requestor"


    class azure.mgmt.authorization.models.RecordAllDecisionsProperties(_Model):
        decision: Optional[Union[str, RecordAllDecisionsResult]]
        justification: Optional[str]
        principal_id: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                decision: Optional[Union[str, RecordAllDecisionsResult]] = ..., 
                justification: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RecordAllDecisionsResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVE = "Approve"
        DENY = "Deny"


    class azure.mgmt.authorization.models.RequestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN_ASSIGN = "AdminAssign"
        ADMIN_EXTEND = "AdminExtend"
        ADMIN_REMOVE = "AdminRemove"
        ADMIN_RENEW = "AdminRenew"
        ADMIN_UPDATE = "AdminUpdate"
        SELF_ACTIVATE = "SelfActivate"
        SELF_DEACTIVATE = "SelfDeactivate"
        SELF_EXTEND = "SelfExtend"
        SELF_RENEW = "SelfRenew"


    class azure.mgmt.authorization.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.authorization.models.ResourceType(_Model):
        display_name: Optional[str]
        name: Optional[str]
        operations: Optional[list[ProviderOperation]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[ProviderOperation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignment(ExtensionResource):
        id: str
        name: str
        properties: Optional[RoleAssignmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentCreateParameters(_Model):
        properties: RoleAssignmentProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: RoleAssignmentProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentProperties(_Model):
        condition: Optional[str]
        condition_version: Optional[str]
        created_by: Optional[str]
        created_on: Optional[datetime]
        delegated_managed_identity_resource_id: Optional[str]
        description: Optional[str]
        principal_id: str
        principal_type: Optional[Union[str, PrincipalType]]
        role_definition_id: str
        scope: Optional[str]
        updated_by: Optional[str]
        updated_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ..., 
                condition_version: Optional[str] = ..., 
                delegated_managed_identity_resource_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                principal_id: str, 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                role_definition_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentSchedule(ExtensionResource):
        id: str
        name: str
        properties: Optional[RoleAssignmentScheduleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleAssignmentScheduleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentScheduleInstance(ExtensionResource):
        id: str
        name: str
        properties: Optional[RoleAssignmentScheduleInstanceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleAssignmentScheduleInstanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentScheduleInstanceProperties(_Model):
        assignment_type: Optional[Union[str, AssignmentType]]
        condition: Optional[str]
        condition_version: Optional[str]
        created_on: Optional[datetime]
        end_date_time: Optional[datetime]
        expanded_properties: Optional[ExpandedProperties]
        linked_role_eligibility_schedule_id: Optional[str]
        linked_role_eligibility_schedule_instance_id: Optional[str]
        member_type: Optional[Union[str, MemberType]]
        origin_role_assignment_id: Optional[str]
        principal_id: Optional[str]
        principal_type: Optional[Union[str, PrincipalType]]
        role_assignment_schedule_id: Optional[str]
        role_definition_id: Optional[str]
        scope: Optional[str]
        start_date_time: Optional[datetime]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                assignment_type: Optional[Union[str, AssignmentType]] = ..., 
                condition: Optional[str] = ..., 
                condition_version: Optional[str] = ..., 
                created_on: Optional[datetime] = ..., 
                end_date_time: Optional[datetime] = ..., 
                expanded_properties: Optional[ExpandedProperties] = ..., 
                linked_role_eligibility_schedule_id: Optional[str] = ..., 
                linked_role_eligibility_schedule_instance_id: Optional[str] = ..., 
                member_type: Optional[Union[str, MemberType]] = ..., 
                origin_role_assignment_id: Optional[str] = ..., 
                principal_id: Optional[str] = ..., 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                role_assignment_schedule_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                start_date_time: Optional[datetime] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentScheduleProperties(_Model):
        assignment_type: Optional[Union[str, AssignmentType]]
        condition: Optional[str]
        condition_version: Optional[str]
        created_on: Optional[datetime]
        end_date_time: Optional[datetime]
        expanded_properties: Optional[ExpandedProperties]
        linked_role_eligibility_schedule_id: Optional[str]
        member_type: Optional[Union[str, MemberType]]
        principal_id: Optional[str]
        principal_type: Optional[Union[str, PrincipalType]]
        role_assignment_schedule_request_id: Optional[str]
        role_definition_id: Optional[str]
        scope: Optional[str]
        start_date_time: Optional[datetime]
        status: Optional[Union[str, Status]]
        updated_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                assignment_type: Optional[Union[str, AssignmentType]] = ..., 
                condition: Optional[str] = ..., 
                condition_version: Optional[str] = ..., 
                created_on: Optional[datetime] = ..., 
                end_date_time: Optional[datetime] = ..., 
                expanded_properties: Optional[ExpandedProperties] = ..., 
                linked_role_eligibility_schedule_id: Optional[str] = ..., 
                member_type: Optional[Union[str, MemberType]] = ..., 
                principal_id: Optional[str] = ..., 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                role_assignment_schedule_request_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                start_date_time: Optional[datetime] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                updated_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentScheduleRequest(ExtensionResource):
        id: str
        name: str
        properties: Optional[RoleAssignmentScheduleRequestProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleAssignmentScheduleRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentScheduleRequestProperties(_Model):
        approval_id: Optional[str]
        condition: Optional[str]
        condition_version: Optional[str]
        created_on: Optional[datetime]
        expanded_properties: Optional[ExpandedProperties]
        justification: Optional[str]
        linked_role_eligibility_schedule_id: Optional[str]
        principal_id: str
        principal_type: Optional[Union[str, PrincipalType]]
        request_type: Union[str, RequestType]
        requestor_id: Optional[str]
        role_definition_id: str
        schedule_info: Optional[RoleAssignmentScheduleRequestPropertiesScheduleInfo]
        scope: Optional[str]
        status: Optional[Union[str, Status]]
        target_role_assignment_schedule_id: Optional[str]
        target_role_assignment_schedule_instance_id: Optional[str]
        ticket_info: Optional[RoleAssignmentScheduleRequestPropertiesTicketInfo]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ..., 
                condition_version: Optional[str] = ..., 
                justification: Optional[str] = ..., 
                linked_role_eligibility_schedule_id: Optional[str] = ..., 
                principal_id: str, 
                request_type: Union[str, RequestType], 
                role_definition_id: str, 
                schedule_info: Optional[RoleAssignmentScheduleRequestPropertiesScheduleInfo] = ..., 
                target_role_assignment_schedule_id: Optional[str] = ..., 
                target_role_assignment_schedule_instance_id: Optional[str] = ..., 
                ticket_info: Optional[RoleAssignmentScheduleRequestPropertiesTicketInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentScheduleRequestPropertiesScheduleInfo(_Model):
        expiration: Optional[RoleAssignmentScheduleRequestPropertiesScheduleInfoExpiration]
        start_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                expiration: Optional[RoleAssignmentScheduleRequestPropertiesScheduleInfoExpiration] = ..., 
                start_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentScheduleRequestPropertiesScheduleInfoExpiration(_Model):
        duration: Optional[str]
        end_date_time: Optional[datetime]
        type: Optional[Union[str, Type]]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[str] = ..., 
                end_date_time: Optional[datetime] = ..., 
                type: Optional[Union[str, Type]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleAssignmentScheduleRequestPropertiesTicketInfo(_Model):
        ticket_number: Optional[str]
        ticket_system: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ticket_number: Optional[str] = ..., 
                ticket_system: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[RoleDefinitionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleDefinitionProperties(_Model):
        assignable_scopes: Optional[list[str]]
        created_by: Optional[str]
        created_on: Optional[datetime]
        description: Optional[str]
        permissions: Optional[list[Permission]]
        role_name: Optional[str]
        role_type: Optional[str]
        updated_by: Optional[str]
        updated_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                assignable_scopes: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                permissions: Optional[list[Permission]] = ..., 
                role_name: Optional[str] = ..., 
                role_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleEligibilitySchedule(ExtensionResource):
        id: str
        name: str
        properties: Optional[RoleEligibilityScheduleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleEligibilityScheduleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleEligibilityScheduleInstance(ExtensionResource):
        id: str
        name: str
        properties: Optional[RoleEligibilityScheduleInstanceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleEligibilityScheduleInstanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleEligibilityScheduleInstanceProperties(_Model):
        condition: Optional[str]
        condition_version: Optional[str]
        created_on: Optional[datetime]
        end_date_time: Optional[datetime]
        expanded_properties: Optional[ExpandedProperties]
        member_type: Optional[Union[str, MemberType]]
        principal_id: Optional[str]
        principal_type: Optional[Union[str, PrincipalType]]
        role_definition_id: Optional[str]
        role_eligibility_schedule_id: Optional[str]
        scope: Optional[str]
        start_date_time: Optional[datetime]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ..., 
                condition_version: Optional[str] = ..., 
                created_on: Optional[datetime] = ..., 
                end_date_time: Optional[datetime] = ..., 
                expanded_properties: Optional[ExpandedProperties] = ..., 
                member_type: Optional[Union[str, MemberType]] = ..., 
                principal_id: Optional[str] = ..., 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                role_definition_id: Optional[str] = ..., 
                role_eligibility_schedule_id: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                start_date_time: Optional[datetime] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleEligibilityScheduleProperties(_Model):
        condition: Optional[str]
        condition_version: Optional[str]
        created_on: Optional[datetime]
        end_date_time: Optional[datetime]
        expanded_properties: Optional[ExpandedProperties]
        member_type: Optional[Union[str, MemberType]]
        principal_id: Optional[str]
        principal_type: Optional[Union[str, PrincipalType]]
        role_definition_id: Optional[str]
        role_eligibility_schedule_request_id: Optional[str]
        scope: Optional[str]
        start_date_time: Optional[datetime]
        status: Optional[Union[str, Status]]
        updated_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ..., 
                condition_version: Optional[str] = ..., 
                created_on: Optional[datetime] = ..., 
                end_date_time: Optional[datetime] = ..., 
                expanded_properties: Optional[ExpandedProperties] = ..., 
                member_type: Optional[Union[str, MemberType]] = ..., 
                principal_id: Optional[str] = ..., 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                role_definition_id: Optional[str] = ..., 
                role_eligibility_schedule_request_id: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                start_date_time: Optional[datetime] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                updated_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleEligibilityScheduleRequest(ExtensionResource):
        id: str
        name: str
        properties: Optional[RoleEligibilityScheduleRequestProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleEligibilityScheduleRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleEligibilityScheduleRequestProperties(_Model):
        approval_id: Optional[str]
        condition: Optional[str]
        condition_version: Optional[str]
        created_on: Optional[datetime]
        expanded_properties: Optional[ExpandedProperties]
        justification: Optional[str]
        principal_id: str
        principal_type: Optional[Union[str, PrincipalType]]
        request_type: Union[str, RequestType]
        requestor_id: Optional[str]
        role_definition_id: str
        schedule_info: Optional[RoleEligibilityScheduleRequestPropertiesScheduleInfo]
        scope: Optional[str]
        status: Optional[Union[str, Status]]
        target_role_eligibility_schedule_id: Optional[str]
        target_role_eligibility_schedule_instance_id: Optional[str]
        ticket_info: Optional[RoleEligibilityScheduleRequestPropertiesTicketInfo]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ..., 
                condition_version: Optional[str] = ..., 
                justification: Optional[str] = ..., 
                principal_id: str, 
                request_type: Union[str, RequestType], 
                role_definition_id: str, 
                schedule_info: Optional[RoleEligibilityScheduleRequestPropertiesScheduleInfo] = ..., 
                target_role_eligibility_schedule_id: Optional[str] = ..., 
                target_role_eligibility_schedule_instance_id: Optional[str] = ..., 
                ticket_info: Optional[RoleEligibilityScheduleRequestPropertiesTicketInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleEligibilityScheduleRequestPropertiesScheduleInfo(_Model):
        expiration: Optional[RoleEligibilityScheduleRequestPropertiesScheduleInfoExpiration]
        start_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                expiration: Optional[RoleEligibilityScheduleRequestPropertiesScheduleInfoExpiration] = ..., 
                start_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleEligibilityScheduleRequestPropertiesScheduleInfoExpiration(_Model):
        duration: Optional[str]
        end_date_time: Optional[datetime]
        type: Optional[Union[str, Type]]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[str] = ..., 
                end_date_time: Optional[datetime] = ..., 
                type: Optional[Union[str, Type]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleEligibilityScheduleRequestPropertiesTicketInfo(_Model):
        ticket_number: Optional[str]
        ticket_system: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ticket_number: Optional[str] = ..., 
                ticket_system: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicy(ExtensionResource):
        id: str
        name: str
        properties: Optional[RoleManagementPolicyProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleManagementPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyApprovalRule(RoleManagementPolicyRule, discriminator='RoleManagementPolicyApprovalRule'):
        id: str
        rule_type: Literal[RoleManagementPolicyRuleType.ROLE_MANAGEMENT_POLICY_APPROVAL_RULE]
        setting: Optional[ApprovalSettings]
        target: RoleManagementPolicyRuleTarget

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                setting: Optional[ApprovalSettings] = ..., 
                target: Optional[RoleManagementPolicyRuleTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyAssignment(ExtensionResource):
        id: str
        name: str
        properties: Optional[RoleManagementPolicyAssignmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleManagementPolicyAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyAssignmentProperties(_Model):
        effective_rules: Optional[list[RoleManagementPolicyRule]]
        policy_assignment_properties: Optional[PolicyAssignmentProperties]
        policy_id: Optional[str]
        role_definition_id: Optional[str]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                policy_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyAuthenticationContextRule(RoleManagementPolicyRule, discriminator='RoleManagementPolicyAuthenticationContextRule'):
        claim_value: Optional[str]
        id: str
        is_enabled: Optional[bool]
        rule_type: Literal[RoleManagementPolicyRuleType.ROLE_MANAGEMENT_POLICY_AUTHENTICATION_CONTEXT_RULE]
        target: RoleManagementPolicyRuleTarget

        @overload
        def __init__(
                self, 
                *, 
                claim_value: Optional[str] = ..., 
                id: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                target: Optional[RoleManagementPolicyRuleTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyEnablementRule(RoleManagementPolicyRule, discriminator='RoleManagementPolicyEnablementRule'):
        enabled_rules: Optional[list[Union[str, EnablementRules]]]
        id: str
        rule_type: Literal[RoleManagementPolicyRuleType.ROLE_MANAGEMENT_POLICY_ENABLEMENT_RULE]
        target: RoleManagementPolicyRuleTarget

        @overload
        def __init__(
                self, 
                *, 
                enabled_rules: Optional[list[Union[str, EnablementRules]]] = ..., 
                id: Optional[str] = ..., 
                target: Optional[RoleManagementPolicyRuleTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyExpirationRule(RoleManagementPolicyRule, discriminator='RoleManagementPolicyExpirationRule'):
        exception_members: Optional[list[UserSet]]
        id: str
        is_expiration_required: Optional[bool]
        maximum_duration: Optional[str]
        rule_type: Literal[RoleManagementPolicyRuleType.ROLE_MANAGEMENT_POLICY_EXPIRATION_RULE]
        target: RoleManagementPolicyRuleTarget

        @overload
        def __init__(
                self, 
                *, 
                exception_members: Optional[list[UserSet]] = ..., 
                id: Optional[str] = ..., 
                is_expiration_required: Optional[bool] = ..., 
                maximum_duration: Optional[str] = ..., 
                target: Optional[RoleManagementPolicyRuleTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyNotificationRule(RoleManagementPolicyRule, discriminator='RoleManagementPolicyNotificationRule'):
        id: str
        is_default_recipients_enabled: Optional[bool]
        notification_level: Optional[Union[str, NotificationLevel]]
        notification_recipients: Optional[list[str]]
        notification_type: Optional[Union[str, NotificationDeliveryMechanism]]
        recipient_type: Optional[Union[str, RecipientType]]
        rule_type: Literal[RoleManagementPolicyRuleType.ROLE_MANAGEMENT_POLICY_NOTIFICATION_RULE]
        target: RoleManagementPolicyRuleTarget

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                is_default_recipients_enabled: Optional[bool] = ..., 
                notification_level: Optional[Union[str, NotificationLevel]] = ..., 
                notification_recipients: Optional[list[str]] = ..., 
                notification_type: Optional[Union[str, NotificationDeliveryMechanism]] = ..., 
                recipient_type: Optional[Union[str, RecipientType]] = ..., 
                target: Optional[RoleManagementPolicyRuleTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyPimOnlyModeRule(RoleManagementPolicyRule, discriminator='RoleManagementPolicyPimOnlyModeRule'):
        id: str
        pim_only_mode_settings: Optional[PIMOnlyModeSettings]
        rule_type: Literal[RoleManagementPolicyRuleType.ROLE_MANAGEMENT_POLICY_PIM_ONLY_MODE_RULE]
        target: RoleManagementPolicyRuleTarget

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                pim_only_mode_settings: Optional[PIMOnlyModeSettings] = ..., 
                target: Optional[RoleManagementPolicyRuleTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        effective_rules: Optional[list[RoleManagementPolicyRule]]
        is_organization_default: Optional[bool]
        last_modified_by: Optional[Principal]
        last_modified_date_time: Optional[datetime]
        policy_properties: Optional[PolicyProperties]
        rules: Optional[list[RoleManagementPolicyRule]]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                is_organization_default: Optional[bool] = ..., 
                rules: Optional[list[RoleManagementPolicyRule]] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyRule(_Model):
        id: Optional[str]
        rule_type: str
        target: Optional[RoleManagementPolicyRuleTarget]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                rule_type: str, 
                target: Optional[RoleManagementPolicyRuleTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyRuleTarget(_Model):
        caller: Optional[str]
        enforced_settings: Optional[list[str]]
        inheritable_settings: Optional[list[str]]
        level: Optional[str]
        operations: Optional[list[str]]
        target_objects: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                caller: Optional[str] = ..., 
                enforced_settings: Optional[list[str]] = ..., 
                inheritable_settings: Optional[list[str]] = ..., 
                level: Optional[str] = ..., 
                operations: Optional[list[str]] = ..., 
                target_objects: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.RoleManagementPolicyRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ROLE_MANAGEMENT_POLICY_APPROVAL_RULE = "RoleManagementPolicyApprovalRule"
        ROLE_MANAGEMENT_POLICY_AUTHENTICATION_CONTEXT_RULE = "RoleManagementPolicyAuthenticationContextRule"
        ROLE_MANAGEMENT_POLICY_ENABLEMENT_RULE = "RoleManagementPolicyEnablementRule"
        ROLE_MANAGEMENT_POLICY_EXPIRATION_RULE = "RoleManagementPolicyExpirationRule"
        ROLE_MANAGEMENT_POLICY_NOTIFICATION_RULE = "RoleManagementPolicyNotificationRule"
        ROLE_MANAGEMENT_POLICY_PIM_ONLY_MODE_RULE = "RoleManagementPolicyPimOnlyModeRule"


    class azure.mgmt.authorization.models.SettableResource(_Model):
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


    class azure.mgmt.authorization.models.SeverityLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.authorization.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        ADMIN_APPROVED = "AdminApproved"
        ADMIN_DENIED = "AdminDenied"
        CANCELED = "Canceled"
        DENIED = "Denied"
        FAILED = "Failed"
        FAILED_AS_RESOURCE_IS_LOCKED = "FailedAsResourceIsLocked"
        GRANTED = "Granted"
        INVALID = "Invalid"
        PENDING_ADMIN_DECISION = "PendingAdminDecision"
        PENDING_APPROVAL = "PendingApproval"
        PENDING_APPROVAL_PROVISIONING = "PendingApprovalProvisioning"
        PENDING_EVALUATION = "PendingEvaluation"
        PENDING_EXTERNAL_PROVISIONING = "PendingExternalProvisioning"
        PENDING_PROVISIONING = "PendingProvisioning"
        PENDING_REVOCATION = "PendingRevocation"
        PENDING_SCHEDULE_CREATION = "PendingScheduleCreation"
        PROVISIONED = "Provisioned"
        PROVISIONING_STARTED = "ProvisioningStarted"
        REVOKED = "Revoked"
        SCHEDULE_CREATED = "ScheduleCreated"
        TIMED_OUT = "TimedOut"


    class azure.mgmt.authorization.models.SystemData(_Model):
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


    class azure.mgmt.authorization.models.TooManyOwnersAssignedToResourceAlertConfigurationProperties(AlertConfigurationProperties, discriminator='TooManyOwnersAssignedToResourceAlertConfiguration'):
        alert_configuration_type: Literal["TooManyOwnersAssignedToResourceAlertConfiguration"]
        alert_definition: AlertDefinition
        alert_definition_id: str
        is_enabled: bool
        scope: str
        threshold_number_of_owners: Optional[int]
        threshold_percentage_of_owners_out_of_all_role_members: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ..., 
                threshold_number_of_owners: Optional[int] = ..., 
                threshold_percentage_of_owners_out_of_all_role_members: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.TooManyOwnersAssignedToResourceAlertIncidentProperties(AlertIncidentProperties, discriminator='TooManyOwnersAssignedToResourceAlertIncident'):
        alert_incident_type: Literal["TooManyOwnersAssignedToResourceAlertIncident"]
        assignee_name: Optional[str]
        assignee_type: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.TooManyPermanentOwnersAssignedToResourceAlertConfigurationProperties(AlertConfigurationProperties, discriminator='TooManyPermanentOwnersAssignedToResourceAlertConfiguration'):
        alert_configuration_type: Literal["TooManyPermanentOwnersAssignedToResourceAlertConfiguration"]
        alert_definition: AlertDefinition
        alert_definition_id: str
        is_enabled: bool
        scope: str
        threshold_number_of_permanent_owners: Optional[int]
        threshold_percentage_of_permanent_owners_out_of_all_owners: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ..., 
                threshold_number_of_permanent_owners: Optional[int] = ..., 
                threshold_percentage_of_permanent_owners_out_of_all_owners: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.TooManyPermanentOwnersAssignedToResourceAlertIncidentProperties(AlertIncidentProperties, discriminator='TooManyPermanentOwnersAssignedToResourceAlertIncident'):
        alert_incident_type: Literal["TooManyPermanentOwnersAssignedToResourceAlertIncident"]
        assignee_name: Optional[str]
        assignee_type: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFTER_DATE_TIME = "AfterDateTime"
        AFTER_DURATION = "AfterDuration"
        NO_EXPIRATION = "NoExpiration"


    class azure.mgmt.authorization.models.UserSet(_Model):
        description: Optional[str]
        id: Optional[str]
        is_backup: Optional[bool]
        user_type: Optional[Union[str, CommonUserType]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                is_backup: Optional[bool] = ..., 
                user_type: Optional[Union[str, CommonUserType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.authorization.models.UserType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "Group"
        SERVICE_PRINCIPAL = "ServicePrincipal"
        USER = "User"


    class azure.mgmt.authorization.models.UsersOrServicePrincipalSet(_Model):
        display_name: Optional[str]
        id: Optional[str]
        type: Optional[Union[str, UserType]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                type: Optional[Union[str, UserType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.authorization.operations

    class azure.mgmt.authorization.operations.AccessReviewDefaultSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(self, **kwargs: Any) -> AccessReviewDefaultSettings: ...

        @overload
        def put(
                self, 
                properties: AccessReviewScheduleSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...

        @overload
        def put(
                self, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...

        @overload
        def put(
                self, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...


    class azure.mgmt.authorization.operations.AccessReviewHistoryDefinitionInstanceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def generate_download_uri(
                self, 
                history_definition_id: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AccessReviewHistoryInstance: ...


    class azure.mgmt.authorization.operations.AccessReviewHistoryDefinitionInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewHistoryInstance]: ...


    class azure.mgmt.authorization.operations.AccessReviewHistoryDefinitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                history_definition_id: str, 
                properties: AccessReviewHistoryDefinitionProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @overload
        def create(
                self, 
                history_definition_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @overload
        def create(
                self, 
                history_definition_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @distributed_trace
        def delete_by_id(
                self, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.operations.AccessReviewHistoryDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_id(
                self, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewHistoryDefinition]: ...


    class azure.mgmt.authorization.operations.AccessReviewInstanceContactedReviewersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewContactedReviewer]: ...


    class azure.mgmt.authorization.operations.AccessReviewInstanceDecisionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewDecision]: ...


    class azure.mgmt.authorization.operations.AccessReviewInstanceMyDecisionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_id(
                self, 
                schedule_definition_id: str, 
                id: str, 
                decision_id: str, 
                **kwargs: Any
            ) -> AccessReviewDecision: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewDecision]: ...

        @overload
        def patch(
                self, 
                schedule_definition_id: str, 
                id: str, 
                decision_id: str, 
                properties: AccessReviewDecisionProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDecision: ...

        @overload
        def patch(
                self, 
                schedule_definition_id: str, 
                id: str, 
                decision_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDecision: ...

        @overload
        def patch(
                self, 
                schedule_definition_id: str, 
                id: str, 
                decision_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDecision: ...


    class azure.mgmt.authorization.operations.AccessReviewInstanceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def accept_recommendations(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def apply_decisions(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def reset_decisions(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def send_reminders(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def stop(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.operations.AccessReviewInstancesAssignedForMyApprovalOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_id(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewInstance]: ...


    class azure.mgmt.authorization.operations.AccessReviewInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                schedule_definition_id: str, 
                id: str, 
                properties: AccessReviewInstanceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @overload
        def create(
                self, 
                schedule_definition_id: str, 
                id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @overload
        def create(
                self, 
                schedule_definition_id: str, 
                id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @distributed_trace
        def get_by_id(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewInstance]: ...


    class azure.mgmt.authorization.operations.AccessReviewScheduleDefinitionsAssignedForMyApprovalOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewScheduleDefinition]: ...


    class azure.mgmt.authorization.operations.AccessReviewScheduleDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update_by_id(
                self, 
                schedule_definition_id: str, 
                properties: AccessReviewScheduleDefinitionProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @overload
        def create_or_update_by_id(
                self, 
                schedule_definition_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @overload
        def create_or_update_by_id(
                self, 
                schedule_definition_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @distributed_trace
        def delete_by_id(
                self, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_by_id(
                self, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewScheduleDefinition]: ...

        @distributed_trace
        def stop(
                self, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.operations.AlertConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                alert_id: str, 
                **kwargs: Any
            ) -> AlertConfiguration: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[AlertConfiguration]: ...

        @overload
        def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: AlertConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.operations.AlertDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                alert_definition_id: str, 
                **kwargs: Any
            ) -> AlertDefinition: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[AlertDefinition]: ...


    class azure.mgmt.authorization.operations.AlertIncidentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                alert_id: str, 
                alert_incident_id: str, 
                **kwargs: Any
            ) -> AlertIncident: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                alert_id: str, 
                **kwargs: Any
            ) -> ItemPaged[AlertIncident]: ...

        @distributed_trace
        def remediate(
                self, 
                scope: str, 
                alert_id: str, 
                alert_incident_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.operations.AlertOperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> AlertOperationResult: ...


    class azure.mgmt.authorization.operations.AlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_refresh(
                self, 
                scope: str, 
                alert_id: str, 
                **kwargs: Any
            ) -> LROPoller[AlertOperationResult]: ...

        @distributed_trace
        def begin_refresh_all(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> LROPoller[AlertOperationResult]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                alert_id: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[Alert]: ...

        @overload
        def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: Alert, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.operations.AttributeNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                attribute_namespace: str, 
                parameters: AttributeNamespaceCreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttributeNamespace: ...

        @overload
        def create(
                self, 
                attribute_namespace: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttributeNamespace: ...

        @overload
        def create(
                self, 
                attribute_namespace: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AttributeNamespace: ...

        @distributed_trace
        def delete(
                self, 
                attribute_namespace: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                attribute_namespace: str, 
                **kwargs: Any
            ) -> AttributeNamespace: ...


    class azure.mgmt.authorization.operations.ClassicAdministratorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ClassicAdministrator]: ...


    class azure.mgmt.authorization.operations.DenyAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                deny_assignment_id: str, 
                parameters: DenyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DenyAssignment: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                deny_assignment_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DenyAssignment: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                deny_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DenyAssignment: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                deny_assignment_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                deny_assignment_id: str, 
                **kwargs: Any
            ) -> DenyAssignment: ...

        @distributed_trace
        def get_by_id(
                self, 
                deny_assignment_id: str, 
                **kwargs: Any
            ) -> DenyAssignment: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DenyAssignment]: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DenyAssignment]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DenyAssignment]: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DenyAssignment]: ...


    class azure.mgmt.authorization.operations.EligibleChildResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EligibleChildResource]: ...


    class azure.mgmt.authorization.operations.GlobalAdministratorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def elevate_access(self, **kwargs: Any) -> None: ...


    class azure.mgmt.authorization.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.authorization.operations.PermissionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Permission]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Permission]: ...


    class azure.mgmt.authorization.operations.ProviderOperationsMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_provider_namespace: str, 
                *, 
                expand: str = "resourceTypes", 
                **kwargs: Any
            ) -> ProviderOperationsMetadata: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: str = "resourceTypes", 
                **kwargs: Any
            ) -> ItemPaged[ProviderOperationsMetadata]: ...


    class azure.mgmt.authorization.operations.RoleAssignmentScheduleInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                role_assignment_schedule_instance_name: str, 
                **kwargs: Any
            ) -> RoleAssignmentScheduleInstance: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleAssignmentScheduleInstance]: ...


    class azure.mgmt.authorization.operations.RoleAssignmentScheduleRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: RoleAssignmentScheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleAssignmentScheduleRequest]: ...

        @overload
        def validate(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: RoleAssignmentScheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @overload
        def validate(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...

        @overload
        def validate(
                self, 
                scope: str, 
                role_assignment_schedule_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignmentScheduleRequest: ...


    class azure.mgmt.authorization.operations.RoleAssignmentSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                role_assignment_schedule_name: str, 
                **kwargs: Any
            ) -> RoleAssignmentSchedule: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleAssignmentSchedule]: ...


    class azure.mgmt.authorization.operations.RoleAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_assignment_name: str, 
                parameters: RoleAssignmentCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @overload
        def create_by_id(
                self, 
                role_assignment_id: str, 
                parameters: RoleAssignmentCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @overload
        def create_by_id(
                self, 
                role_assignment_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @overload
        def create_by_id(
                self, 
                role_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                role_assignment_name: str, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[RoleAssignment]: ...

        @distributed_trace
        def delete_by_id(
                self, 
                role_assignment_id: str, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[RoleAssignment]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                role_assignment_name: str, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @distributed_trace
        def get_by_id(
                self, 
                role_assignment_id: str, 
                *, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> RoleAssignment: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleAssignment]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleAssignment]: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleAssignment]: ...

        @distributed_trace
        def list_for_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleAssignment]: ...


    class azure.mgmt.authorization.operations.RoleDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                role_definition_id: str, 
                role_definition: RoleDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleDefinition: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                role_definition_id: str, 
                role_definition: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleDefinition: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                role_definition_id: str, 
                role_definition: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleDefinition: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> Optional[RoleDefinition]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                role_definition_id: str, 
                **kwargs: Any
            ) -> RoleDefinition: ...

        @distributed_trace
        def get_by_id(
                self, 
                role_id: str, 
                **kwargs: Any
            ) -> RoleDefinition: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleDefinition]: ...


    class azure.mgmt.authorization.operations.RoleEligibilityScheduleInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                role_eligibility_schedule_instance_name: str, 
                **kwargs: Any
            ) -> RoleEligibilityScheduleInstance: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleEligibilityScheduleInstance]: ...


    class azure.mgmt.authorization.operations.RoleEligibilityScheduleRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: RoleEligibilityScheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleEligibilityScheduleRequest]: ...

        @overload
        def validate(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: RoleEligibilityScheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @overload
        def validate(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...

        @overload
        def validate(
                self, 
                scope: str, 
                role_eligibility_schedule_request_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleEligibilityScheduleRequest: ...


    class azure.mgmt.authorization.operations.RoleEligibilitySchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                role_eligibility_schedule_name: str, 
                **kwargs: Any
            ) -> RoleEligibilitySchedule: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoleEligibilitySchedule]: ...


    class azure.mgmt.authorization.operations.RoleManagementPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                role_management_policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                role_management_policy_name: str, 
                **kwargs: Any
            ) -> RoleManagementPolicy: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[RoleManagementPolicy]: ...

        @overload
        def update(
                self, 
                scope: str, 
                role_management_policy_name: str, 
                parameters: RoleManagementPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicy: ...

        @overload
        def update(
                self, 
                scope: str, 
                role_management_policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicy: ...

        @overload
        def update(
                self, 
                scope: str, 
                role_management_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicy: ...


    class azure.mgmt.authorization.operations.RoleManagementPolicyAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_management_policy_assignment_name: str, 
                parameters: RoleManagementPolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicyAssignment: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_management_policy_assignment_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicyAssignment: ...

        @overload
        def create(
                self, 
                scope: str, 
                role_management_policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleManagementPolicyAssignment: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                role_management_policy_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                role_management_policy_assignment_name: str, 
                **kwargs: Any
            ) -> RoleManagementPolicyAssignment: ...

        @distributed_trace
        def list_for_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[RoleManagementPolicyAssignment]: ...


    class azure.mgmt.authorization.operations.ScopeAccessReviewDefaultSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...

        @overload
        def put(
                self, 
                scope: str, 
                properties: AccessReviewScheduleSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...

        @overload
        def put(
                self, 
                scope: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...

        @overload
        def put(
                self, 
                scope: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewDefaultSettings: ...


    class azure.mgmt.authorization.operations.ScopeAccessReviewHistoryDefinitionInstanceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def generate_download_uri(
                self, 
                scope: str, 
                history_definition_id: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AccessReviewHistoryInstance: ...


    class azure.mgmt.authorization.operations.ScopeAccessReviewHistoryDefinitionInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewHistoryInstance]: ...


    class azure.mgmt.authorization.operations.ScopeAccessReviewHistoryDefinitionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                scope: str, 
                history_definition_id: str, 
                properties: AccessReviewHistoryDefinitionProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @overload
        def create(
                self, 
                scope: str, 
                history_definition_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @overload
        def create(
                self, 
                scope: str, 
                history_definition_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @distributed_trace
        def delete_by_id(
                self, 
                scope: str, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.operations.ScopeAccessReviewHistoryDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_id(
                self, 
                scope: str, 
                history_definition_id: str, 
                **kwargs: Any
            ) -> AccessReviewHistoryDefinition: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewHistoryDefinition]: ...


    class azure.mgmt.authorization.operations.ScopeAccessReviewInstanceContactedReviewersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewContactedReviewer]: ...


    class azure.mgmt.authorization.operations.ScopeAccessReviewInstanceDecisionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewDecision]: ...


    class azure.mgmt.authorization.operations.ScopeAccessReviewInstanceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def apply_decisions(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def record_all_decisions(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: RecordAllDecisionsProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def record_all_decisions(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def record_all_decisions(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def reset_decisions(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def send_reminders(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def stop(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.operations.ScopeAccessReviewInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: AccessReviewInstanceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @overload
        def create(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @overload
        def create(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @distributed_trace
        def get_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> AccessReviewInstance: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewInstance]: ...


    class azure.mgmt.authorization.operations.ScopeAccessReviewScheduleDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                properties: AccessReviewScheduleDefinitionProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @overload
        def create_or_update_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @overload
        def create_or_update_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @distributed_trace
        def delete_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_by_id(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> AccessReviewScheduleDefinition: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewScheduleDefinition]: ...

        @distributed_trace
        def stop(
                self, 
                scope: str, 
                schedule_definition_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.authorization.operations.TenantLevelAccessReviewInstanceContactedReviewersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                schedule_definition_id: str, 
                id: str, 
                **kwargs: Any
            ) -> ItemPaged[AccessReviewContactedReviewer]: ...


```