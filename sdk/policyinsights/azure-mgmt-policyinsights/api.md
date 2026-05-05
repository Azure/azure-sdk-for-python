```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.policyinsights

    class azure.mgmt.policyinsights.PolicyInsightsClient: implements ContextManager 
        attestations: AttestationsOperations
        component_policy_states: ComponentPolicyStatesOperations
        operations: Operations
        policy_events: PolicyEventsOperations
        policy_metadata: PolicyMetadataOperations
        policy_restrictions: PolicyRestrictionsOperations
        policy_states: PolicyStatesOperations
        policy_tracked_resources: PolicyTrackedResourcesOperations
        remediations: RemediationsOperations

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


namespace azure.mgmt.policyinsights.aio

    class azure.mgmt.policyinsights.aio.PolicyInsightsClient: implements AsyncContextManager 
        attestations: AttestationsOperations
        component_policy_states: ComponentPolicyStatesOperations
        operations: Operations
        policy_events: PolicyEventsOperations
        policy_metadata: PolicyMetadataOperations
        policy_restrictions: PolicyRestrictionsOperations
        policy_states: PolicyStatesOperations
        policy_tracked_resources: PolicyTrackedResourcesOperations
        remediations: RemediationsOperations

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


namespace azure.mgmt.policyinsights.aio.operations

    class azure.mgmt.policyinsights.aio.operations.AttestationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update_at_resource(
                self, 
                resource_id: str, 
                attestation_name: str, 
                parameters: Attestation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Attestation]: ...

        @overload
        async def begin_create_or_update_at_resource(
                self, 
                resource_id: str, 
                attestation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Attestation]: ...

        @overload
        async def begin_create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                attestation_name: str, 
                parameters: Attestation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Attestation]: ...

        @overload
        async def begin_create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                attestation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Attestation]: ...

        @overload
        async def begin_create_or_update_at_subscription(
                self, 
                attestation_name: str, 
                parameters: Attestation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Attestation]: ...

        @overload
        async def begin_create_or_update_at_subscription(
                self, 
                attestation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Attestation]: ...

        @distributed_trace_async
        async def delete_at_resource(
                self, 
                resource_id: str, 
                attestation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_resource_group(
                self, 
                resource_group_name: str, 
                attestation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_subscription(
                self, 
                attestation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_at_resource(
                self, 
                resource_id: str, 
                attestation_name: str, 
                **kwargs: Any
            ) -> Attestation: ...

        @distributed_trace_async
        async def get_at_resource_group(
                self, 
                resource_group_name: str, 
                attestation_name: str, 
                **kwargs: Any
            ) -> Attestation: ...

        @distributed_trace_async
        async def get_at_subscription(
                self, 
                attestation_name: str, 
                **kwargs: Any
            ) -> Attestation: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Attestation]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Attestation]: ...

        @distributed_trace
        def list_for_subscription(
                self, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Attestation]: ...


    class azure.mgmt.policyinsights.aio.operations.ComponentPolicyStatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_query_results_for_policy_definition(
                self, 
                subscription_id: str, 
                policy_definition_name: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...

        @distributed_trace_async
        async def list_query_results_for_resource(
                self, 
                resource_id: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...

        @distributed_trace_async
        async def list_query_results_for_resource_group(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...

        @distributed_trace_async
        async def list_query_results_for_resource_group_level_policy_assignment(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                policy_assignment_name: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...

        @distributed_trace_async
        async def list_query_results_for_subscription(
                self, 
                subscription_id: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...

        @distributed_trace_async
        async def list_query_results_for_subscription_level_policy_assignment(
                self, 
                subscription_id: str, 
                policy_assignment_name: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...


    class azure.mgmt.policyinsights.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(self, **kwargs: Any) -> OperationsListResults: ...


    class azure.mgmt.policyinsights.aio.operations.PolicyEventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_query_results_for_management_group(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                management_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_policy_definition(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                policy_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_policy_set_definition(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                policy_set_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_resource(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                resource_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_resource_group(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                resource_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_resource_group_level_policy_assignment(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                resource_group_name: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_subscription(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_subscription_level_policy_assignment(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEvent]: ...


    class azure.mgmt.policyinsights.aio.operations.PolicyMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_resource(
                self, 
                resource_name: str, 
                **kwargs: Any
            ) -> PolicyMetadata: ...

        @distributed_trace
        def list(
                self, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[SlimPolicyMetadata]: ...


    class azure.mgmt.policyinsights.aio.operations.PolicyRestrictionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_at_management_group_scope(
                self, 
                management_group_id: str, 
                parameters: CheckManagementGroupRestrictionsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...

        @overload
        async def check_at_management_group_scope(
                self, 
                management_group_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...

        @overload
        async def check_at_resource_group_scope(
                self, 
                resource_group_name: str, 
                parameters: CheckRestrictionsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...

        @overload
        async def check_at_resource_group_scope(
                self, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...

        @overload
        async def check_at_subscription_scope(
                self, 
                parameters: CheckRestrictionsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...

        @overload
        async def check_at_subscription_scope(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...


    class azure.mgmt.policyinsights.aio.operations.PolicyStatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_trigger_resource_group_evaluation(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_trigger_subscription_evaluation(
                self, 
                subscription_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        def list_query_results_for_management_group(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                management_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_policy_definition(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                policy_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_policy_set_definition(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                policy_set_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_resource(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                resource_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_resource_group(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                resource_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_resource_group_level_policy_assignment(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                resource_group_name: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_subscription(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_subscription_level_policy_assignment(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyState]: ...

        @distributed_trace_async
        async def summarize_for_management_group(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                management_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace_async
        async def summarize_for_policy_definition(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                policy_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace_async
        async def summarize_for_policy_set_definition(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                policy_set_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace_async
        async def summarize_for_resource(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                resource_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace_async
        async def summarize_for_resource_group(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                resource_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace_async
        async def summarize_for_resource_group_level_policy_assignment(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                resource_group_name: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace_async
        async def summarize_for_subscription(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace_async
        async def summarize_for_subscription_level_policy_assignment(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...


    class azure.mgmt.policyinsights.aio.operations.PolicyTrackedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_query_results_for_management_group(
                self, 
                management_group_name: str, 
                policy_tracked_resources_resource: Union[str, PolicyTrackedResourcesResourceType], 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyTrackedResource]: ...

        @distributed_trace
        def list_query_results_for_resource(
                self, 
                resource_id: str, 
                policy_tracked_resources_resource: Union[str, PolicyTrackedResourcesResourceType], 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyTrackedResource]: ...

        @distributed_trace
        def list_query_results_for_resource_group(
                self, 
                resource_group_name: str, 
                policy_tracked_resources_resource: Union[str, PolicyTrackedResourcesResourceType], 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyTrackedResource]: ...

        @distributed_trace
        def list_query_results_for_subscription(
                self, 
                policy_tracked_resources_resource: Union[str, PolicyTrackedResourcesResourceType], 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyTrackedResource]: ...


    class azure.mgmt.policyinsights.aio.operations.RemediationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace_async
        async def cancel_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace_async
        async def cancel_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace_async
        async def cancel_at_subscription(
                self, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                parameters: Remediation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        async def create_or_update_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                parameters: Remediation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        async def create_or_update_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        async def create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                parameters: Remediation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        async def create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        async def create_or_update_at_subscription(
                self, 
                remediation_name: str, 
                parameters: Remediation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        async def create_or_update_at_subscription(
                self, 
                remediation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace_async
        async def delete_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Optional[Remediation]: ...

        @distributed_trace_async
        async def delete_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Optional[Remediation]: ...

        @distributed_trace_async
        async def delete_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Optional[Remediation]: ...

        @distributed_trace_async
        async def delete_at_subscription(
                self, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Optional[Remediation]: ...

        @distributed_trace_async
        async def get_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace_async
        async def get_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace_async
        async def get_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace_async
        async def get_at_subscription(
                self, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace
        def list_deployments_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RemediationDeployment]: ...

        @distributed_trace
        def list_deployments_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RemediationDeployment]: ...

        @distributed_trace
        def list_deployments_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RemediationDeployment]: ...

        @distributed_trace
        def list_deployments_at_subscription(
                self, 
                remediation_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RemediationDeployment]: ...

        @distributed_trace
        def list_for_management_group(
                self, 
                management_group_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Remediation]: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Remediation]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Remediation]: ...

        @distributed_trace
        def list_for_subscription(
                self, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Remediation]: ...


namespace azure.mgmt.policyinsights.models

    class azure.mgmt.policyinsights.models.Attestation(Resource):
        assessment_date: datetime
        comments: str
        compliance_state: Union[str, ComplianceState]
        evidence: list[AttestationEvidence]
        expires_on: datetime
        id: str
        last_compliance_state_change_at: datetime
        metadata: JSON
        name: str
        owner: str
        policy_assignment_id: str
        policy_definition_reference_id: str
        provisioning_state: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_date: Optional[datetime] = ..., 
                comments: Optional[str] = ..., 
                compliance_state: Optional[Union[str, ComplianceState]] = ..., 
                evidence: Optional[List[AttestationEvidence]] = ..., 
                expires_on: Optional[datetime] = ..., 
                metadata: Optional[JSON] = ..., 
                owner: Optional[str] = ..., 
                policy_assignment_id: str, 
                policy_definition_reference_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.AttestationEvidence(Model):
        description: str
        source_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                source_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.AttestationListResult(Model):
        next_link: str
        value: list[Attestation]

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


    class azure.mgmt.policyinsights.models.CheckManagementGroupRestrictionsRequest(Model):
        pending_fields: list[PendingField]
        resource_details: CheckRestrictionsResourceDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                pending_fields: Optional[List[PendingField]] = ..., 
                resource_details: Optional[CheckRestrictionsResourceDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.CheckRestrictionEvaluationDetails(Model):
        evaluated_expressions: list[ExpressionEvaluationDetails]
        if_not_exists_details: IfNotExistsEvaluationDetails
        reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                evaluated_expressions: Optional[List[ExpressionEvaluationDetails]] = ..., 
                if_not_exists_details: Optional[IfNotExistsEvaluationDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.CheckRestrictionsRequest(Model):
        include_audit_effect: bool
        pending_fields: list[PendingField]
        resource_details: CheckRestrictionsResourceDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                include_audit_effect: bool = False, 
                pending_fields: Optional[List[PendingField]] = ..., 
                resource_details: CheckRestrictionsResourceDetails, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.CheckRestrictionsResourceDetails(Model):
        api_version: str
        resource_content: JSON
        scope: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                resource_content: JSON, 
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


    class azure.mgmt.policyinsights.models.CheckRestrictionsResult(Model):
        content_evaluation_result: CheckRestrictionsResultContentEvaluationResult
        field_restrictions: list[FieldRestrictions]

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


    class azure.mgmt.policyinsights.models.CheckRestrictionsResultContentEvaluationResult(Model):
        policy_evaluations: list[PolicyEvaluationResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                policy_evaluations: Optional[List[PolicyEvaluationResult]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.ComplianceDetail(Model):
        compliance_state: str
        count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compliance_state: Optional[str] = ..., 
                count: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.ComplianceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANT = "Compliant"
        NON_COMPLIANT = "NonCompliant"
        UNKNOWN = "Unknown"


    class azure.mgmt.policyinsights.models.ComponentEventDetails(Model):
        additional_properties: dict[str, any]
        id: str
        name: str
        policy_definition_action: str
        principal_oid: str
        tenant_id: str
        timestamp: datetime
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                policy_definition_action: Optional[str] = ..., 
                principal_oid: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                timestamp: Optional[datetime] = ..., 
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


    class azure.mgmt.policyinsights.models.ComponentExpressionEvaluationDetails(Model):
        expression: str
        expression_kind: str
        expression_value: JSON
        operator: str
        path: str
        result: str
        target_value: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                result: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.ComponentPolicyEvaluationDetails(Model):
        evaluated_expressions: list[ComponentExpressionEvaluationDetails]
        reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reason: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.ComponentPolicyState(Model):
        additional_properties: dict[str, any]
        compliance_state: str
        component_id: str
        component_name: str
        component_type: str
        odata_context: str
        odata_id: str
        policy_assignment_id: str
        policy_assignment_name: str
        policy_assignment_owner: str
        policy_assignment_parameters: str
        policy_assignment_scope: str
        policy_assignment_version: str
        policy_definition_action: str
        policy_definition_category: str
        policy_definition_group_names: list[str]
        policy_definition_id: str
        policy_definition_name: str
        policy_definition_reference_id: str
        policy_definition_version: str
        policy_evaluation_details: ComponentPolicyEvaluationDetails
        policy_set_definition_category: str
        policy_set_definition_id: str
        policy_set_definition_name: str
        policy_set_definition_owner: str
        policy_set_definition_parameters: str
        policy_set_definition_version: str
        resource_group: str
        resource_id: str
        resource_location: str
        resource_type: str
        subscription_id: str
        timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                policy_evaluation_details: Optional[ComponentPolicyEvaluationDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.ComponentPolicyStatesQueryResults(Model):
        odata_context: str
        odata_count: int
        value: list[ComponentPolicyState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                odata_context: Optional[str] = ..., 
                odata_count: Optional[int] = ..., 
                value: Optional[List[ComponentPolicyState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.ComponentPolicyStatesResource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATEST = "latest"


    class azure.mgmt.policyinsights.models.ComponentStateDetails(Model):
        additional_properties: dict[str, any]
        compliance_state: str
        id: str
        name: str
        timestamp: datetime
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                compliance_state: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                timestamp: Optional[datetime] = ..., 
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


    class azure.mgmt.policyinsights.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.policyinsights.models.ErrorDefinition(Model):
        additional_info: list[TypedErrorInfo]
        code: str
        details: list[ErrorDefinition]
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


    class azure.mgmt.policyinsights.models.ErrorDefinitionAutoGenerated(Model):
        additional_info: list[TypedErrorInfo]
        code: str
        details: list[ErrorDefinitionAutoGenerated]
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


    class azure.mgmt.policyinsights.models.ErrorDefinitionAutoGenerated2(Model):
        additional_info: list[TypedErrorInfo]
        code: str
        details: list[ErrorDefinitionAutoGenerated2]
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


    class azure.mgmt.policyinsights.models.ErrorResponse(Model):
        error: ErrorDefinition

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDefinition] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.ErrorResponseAutoGenerated(Model):
        error: ErrorDefinitionAutoGenerated

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDefinitionAutoGenerated] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.ErrorResponseAutoGenerated2(Model):
        error: ErrorDefinitionAutoGenerated2

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDefinitionAutoGenerated2] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.ExpressionEvaluationDetails(Model):
        expression: str
        expression_kind: str
        expression_value: JSON
        operator: str
        path: str
        result: str
        target_value: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expression: Optional[str] = ..., 
                expression_value: Optional[JSON] = ..., 
                operator: Optional[str] = ..., 
                path: Optional[str] = ..., 
                result: Optional[str] = ..., 
                target_value: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.FieldRestriction(Model):
        default_value: str
        policy: PolicyReference
        policy_effect: str
        reason: str
        result: Union[str, FieldRestrictionResult]
        values: list[str]

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


    class azure.mgmt.policyinsights.models.FieldRestrictionResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        DENY = "Deny"
        REMOVED = "Removed"
        REQUIRED = "Required"


    class azure.mgmt.policyinsights.models.FieldRestrictions(Model):
        field: str
        restrictions: list[FieldRestriction]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                restrictions: Optional[List[FieldRestriction]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.IfNotExistsEvaluationDetails(Model):
        resource_id: str
        total_resources: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                total_resources: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
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


    class azure.mgmt.policyinsights.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.OperationsListResults(Model):
        odata_count: int
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                odata_count: Optional[int] = ..., 
                value: Optional[List[Operation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.PendingField(Model):
        field: str
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                field: str, 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.PolicyAssignmentSummary(Model):
        policy_assignment_id: str
        policy_definitions: list[PolicyDefinitionSummary]
        policy_groups: list[PolicyGroupSummary]
        policy_set_definition_id: str
        results: SummaryResults

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                policy_assignment_id: Optional[str] = ..., 
                policy_definitions: Optional[List[PolicyDefinitionSummary]] = ..., 
                policy_groups: Optional[List[PolicyGroupSummary]] = ..., 
                policy_set_definition_id: Optional[str] = ..., 
                results: Optional[SummaryResults] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.PolicyDefinitionSummary(Model):
        effect: str
        policy_definition_group_names: list[str]
        policy_definition_id: str
        policy_definition_reference_id: str
        results: SummaryResults

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                effect: Optional[str] = ..., 
                policy_definition_group_names: Optional[List[str]] = ..., 
                policy_definition_id: Optional[str] = ..., 
                policy_definition_reference_id: Optional[str] = ..., 
                results: Optional[SummaryResults] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.PolicyDetails(Model):
        policy_assignment_display_name: str
        policy_assignment_id: str
        policy_assignment_scope: str
        policy_definition_id: str
        policy_definition_reference_id: str
        policy_set_definition_id: str

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


    class azure.mgmt.policyinsights.models.PolicyEffectDetails(Model):
        policy_effect: str

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


    class azure.mgmt.policyinsights.models.PolicyEvaluationDetails(Model):
        evaluated_expressions: list[ExpressionEvaluationDetails]
        if_not_exists_details: IfNotExistsEvaluationDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                evaluated_expressions: Optional[List[ExpressionEvaluationDetails]] = ..., 
                if_not_exists_details: Optional[IfNotExistsEvaluationDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.PolicyEvaluationResult(Model):
        effect_details: PolicyEffectDetails
        evaluation_details: CheckRestrictionEvaluationDetails
        evaluation_result: str
        policy_info: PolicyReference

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


    class azure.mgmt.policyinsights.models.PolicyEvent(Model):
        additional_properties: dict[str, any]
        compliance_state: str
        components: list[ComponentEventDetails]
        effective_parameters: str
        is_compliant: bool
        management_group_ids: str
        odata_context: str
        odata_id: str
        policy_assignment_id: str
        policy_assignment_name: str
        policy_assignment_owner: str
        policy_assignment_parameters: str
        policy_assignment_scope: str
        policy_definition_action: str
        policy_definition_category: str
        policy_definition_id: str
        policy_definition_name: str
        policy_definition_reference_id: str
        policy_set_definition_category: str
        policy_set_definition_id: str
        policy_set_definition_name: str
        policy_set_definition_owner: str
        policy_set_definition_parameters: str
        principal_oid: str
        resource_group: str
        resource_id: str
        resource_location: str
        resource_tags: str
        resource_type: str
        subscription_id: str
        tenant_id: str
        timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                compliance_state: Optional[str] = ..., 
                components: Optional[List[ComponentEventDetails]] = ..., 
                effective_parameters: Optional[str] = ..., 
                is_compliant: Optional[bool] = ..., 
                management_group_ids: Optional[str] = ..., 
                odata_context: Optional[str] = ..., 
                odata_id: Optional[str] = ..., 
                policy_assignment_id: Optional[str] = ..., 
                policy_assignment_name: Optional[str] = ..., 
                policy_assignment_owner: Optional[str] = ..., 
                policy_assignment_parameters: Optional[str] = ..., 
                policy_assignment_scope: Optional[str] = ..., 
                policy_definition_action: Optional[str] = ..., 
                policy_definition_category: Optional[str] = ..., 
                policy_definition_id: Optional[str] = ..., 
                policy_definition_name: Optional[str] = ..., 
                policy_definition_reference_id: Optional[str] = ..., 
                policy_set_definition_category: Optional[str] = ..., 
                policy_set_definition_id: Optional[str] = ..., 
                policy_set_definition_name: Optional[str] = ..., 
                policy_set_definition_owner: Optional[str] = ..., 
                policy_set_definition_parameters: Optional[str] = ..., 
                principal_oid: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                resource_location: Optional[str] = ..., 
                resource_tags: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.PolicyEventsQueryResults(Model):
        odata_context: str
        odata_count: int
        odata_next_link: str
        value: list[PolicyEvent]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                odata_context: Optional[str] = ..., 
                odata_count: Optional[int] = ..., 
                odata_next_link: Optional[str] = ..., 
                value: Optional[List[PolicyEvent]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.PolicyEventsResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.policyinsights.models.PolicyGroupSummary(Model):
        policy_group_name: str
        results: SummaryResults

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                policy_group_name: Optional[str] = ..., 
                results: Optional[SummaryResults] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.PolicyMetadata(Model):
        additional_content_url: str
        category: str
        description: str
        id: str
        metadata: JSON
        metadata_id: str
        name: str
        owner: str
        requirements: str
        title: str
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


    class azure.mgmt.policyinsights.models.PolicyMetadataCollection(Model):
        next_link: str
        value: list[SlimPolicyMetadata]

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


    class azure.mgmt.policyinsights.models.PolicyMetadataProperties(PolicyMetadataSlimProperties):
        additional_content_url: str
        category: str
        description: str
        metadata: JSON
        metadata_id: str
        owner: str
        requirements: str
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


    class azure.mgmt.policyinsights.models.PolicyMetadataSlimProperties(Model):
        additional_content_url: str
        category: str
        metadata: JSON
        metadata_id: str
        owner: str
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


    class azure.mgmt.policyinsights.models.PolicyReference(Model):
        policy_assignment_id: str
        policy_definition_id: str
        policy_definition_reference_id: str
        policy_set_definition_id: str

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


    class azure.mgmt.policyinsights.models.PolicyState(Model):
        additional_properties: dict[str, any]
        compliance_state: str
        components: list[ComponentStateDetails]
        effective_parameters: str
        is_compliant: bool
        management_group_ids: str
        odata_context: str
        odata_id: str
        policy_assignment_id: str
        policy_assignment_name: str
        policy_assignment_owner: str
        policy_assignment_parameters: str
        policy_assignment_scope: str
        policy_assignment_version: str
        policy_definition_action: str
        policy_definition_category: str
        policy_definition_group_names: list[str]
        policy_definition_id: str
        policy_definition_name: str
        policy_definition_reference_id: str
        policy_definition_version: str
        policy_evaluation_details: PolicyEvaluationDetails
        policy_set_definition_category: str
        policy_set_definition_id: str
        policy_set_definition_name: str
        policy_set_definition_owner: str
        policy_set_definition_parameters: str
        policy_set_definition_version: str
        resource_group: str
        resource_id: str
        resource_location: str
        resource_tags: str
        resource_type: str
        subscription_id: str
        timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                compliance_state: Optional[str] = ..., 
                components: Optional[List[ComponentStateDetails]] = ..., 
                effective_parameters: Optional[str] = ..., 
                is_compliant: Optional[bool] = ..., 
                management_group_ids: Optional[str] = ..., 
                odata_context: Optional[str] = ..., 
                odata_id: Optional[str] = ..., 
                policy_assignment_id: Optional[str] = ..., 
                policy_assignment_name: Optional[str] = ..., 
                policy_assignment_owner: Optional[str] = ..., 
                policy_assignment_parameters: Optional[str] = ..., 
                policy_assignment_scope: Optional[str] = ..., 
                policy_definition_action: Optional[str] = ..., 
                policy_definition_category: Optional[str] = ..., 
                policy_definition_group_names: Optional[List[str]] = ..., 
                policy_definition_id: Optional[str] = ..., 
                policy_definition_name: Optional[str] = ..., 
                policy_definition_reference_id: Optional[str] = ..., 
                policy_evaluation_details: Optional[PolicyEvaluationDetails] = ..., 
                policy_set_definition_category: Optional[str] = ..., 
                policy_set_definition_id: Optional[str] = ..., 
                policy_set_definition_name: Optional[str] = ..., 
                policy_set_definition_owner: Optional[str] = ..., 
                policy_set_definition_parameters: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                resource_location: Optional[str] = ..., 
                resource_tags: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.PolicyStatesQueryResults(Model):
        odata_context: str
        odata_count: int
        odata_next_link: str
        value: list[PolicyState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                odata_context: Optional[str] = ..., 
                odata_count: Optional[int] = ..., 
                odata_next_link: Optional[str] = ..., 
                value: Optional[List[PolicyState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.PolicyStatesResource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"
        LATEST = "latest"


    class azure.mgmt.policyinsights.models.PolicyStatesSummaryResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATEST = "latest"


    class azure.mgmt.policyinsights.models.PolicyTrackedResource(Model):
        created_by: TrackedResourceModificationDetails
        last_modified_by: TrackedResourceModificationDetails
        last_update_utc: datetime
        policy_details: PolicyDetails
        tracked_resource_id: str

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


    class azure.mgmt.policyinsights.models.PolicyTrackedResourcesQueryResults(Model):
        next_link: str
        value: list[PolicyTrackedResource]

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


    class azure.mgmt.policyinsights.models.PolicyTrackedResourcesResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.policyinsights.models.QueryFailure(Model):
        error: QueryFailureError

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[QueryFailureError] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.QueryFailureError(Model):
        code: str
        message: str

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


    class azure.mgmt.policyinsights.models.QueryOptions(Model):
        apply: str
        expand: str
        filter: str
        from_property: datetime
        order_by: str
        select: str
        skip_token: str
        to: datetime
        top: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                apply: Optional[str] = ..., 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                from_property: Optional[datetime] = ..., 
                order_by: Optional[str] = ..., 
                select: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                to: Optional[datetime] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.Remediation(Model):
        correlation_id: str
        created_on: datetime
        deployment_status: RemediationDeploymentSummary
        failure_threshold: RemediationPropertiesFailureThreshold
        filters: RemediationFilters
        id: str
        last_updated_on: datetime
        name: str
        parallel_deployments: int
        policy_assignment_id: str
        policy_definition_reference_id: str
        provisioning_state: str
        resource_count: int
        resource_discovery_mode: Union[str, ResourceDiscoveryMode]
        status_message: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                failure_threshold: Optional[RemediationPropertiesFailureThreshold] = ..., 
                filters: Optional[RemediationFilters] = ..., 
                parallel_deployments: Optional[int] = ..., 
                policy_assignment_id: Optional[str] = ..., 
                policy_definition_reference_id: Optional[str] = ..., 
                resource_count: Optional[int] = ..., 
                resource_discovery_mode: Optional[Union[str, ResourceDiscoveryMode]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.RemediationDeployment(Model):
        created_on: datetime
        deployment_id: str
        error: ErrorDefinition
        last_updated_on: datetime
        remediated_resource_id: str
        resource_location: str
        status: str

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


    class azure.mgmt.policyinsights.models.RemediationDeploymentSummary(Model):
        failed_deployments: int
        successful_deployments: int
        total_deployments: int

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


    class azure.mgmt.policyinsights.models.RemediationDeploymentsListResult(Model):
        next_link: str
        value: list[RemediationDeployment]

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


    class azure.mgmt.policyinsights.models.RemediationFilters(Model):
        locations: list[str]
        resource_ids: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                locations: Optional[List[str]] = ..., 
                resource_ids: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.RemediationListResult(Model):
        next_link: str
        value: list[Remediation]

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


    class azure.mgmt.policyinsights.models.RemediationPropertiesFailureThreshold(Model):
        percentage: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                percentage: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.Resource(Model):
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


    class azure.mgmt.policyinsights.models.ResourceDiscoveryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXISTING_NON_COMPLIANT = "ExistingNonCompliant"
        RE_EVALUATE_COMPLIANCE = "ReEvaluateCompliance"


    class azure.mgmt.policyinsights.models.SlimPolicyMetadata(Model):
        additional_content_url: str
        category: str
        id: str
        metadata: JSON
        metadata_id: str
        name: str
        owner: str
        title: str
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


    class azure.mgmt.policyinsights.models.SummarizeResults(Model):
        odata_context: str
        odata_count: int
        value: list[Summary]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                odata_context: Optional[str] = ..., 
                odata_count: Optional[int] = ..., 
                value: Optional[List[Summary]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.Summary(Model):
        odata_context: str
        odata_id: str
        policy_assignments: list[PolicyAssignmentSummary]
        results: SummaryResults

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                odata_context: Optional[str] = ..., 
                odata_id: Optional[str] = ..., 
                policy_assignments: Optional[List[PolicyAssignmentSummary]] = ..., 
                results: Optional[SummaryResults] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.SummaryResults(Model):
        non_compliant_policies: int
        non_compliant_resources: int
        policy_details: list[ComplianceDetail]
        policy_group_details: list[ComplianceDetail]
        query_results_uri: str
        resource_details: list[ComplianceDetail]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                non_compliant_policies: Optional[int] = ..., 
                non_compliant_resources: Optional[int] = ..., 
                policy_details: Optional[List[ComplianceDetail]] = ..., 
                policy_group_details: Optional[List[ComplianceDetail]] = ..., 
                query_results_uri: Optional[str] = ..., 
                resource_details: Optional[List[ComplianceDetail]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.policyinsights.models.SystemData(Model):
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


    class azure.mgmt.policyinsights.models.TrackedResourceModificationDetails(Model):
        deployment_id: str
        deployment_time: datetime
        policy_details: PolicyDetails

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


    class azure.mgmt.policyinsights.models.TypedErrorInfo(Model):
        info: any
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


namespace azure.mgmt.policyinsights.operations

    class azure.mgmt.policyinsights.operations.AttestationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update_at_resource(
                self, 
                resource_id: str, 
                attestation_name: str, 
                parameters: Attestation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Attestation]: ...

        @overload
        def begin_create_or_update_at_resource(
                self, 
                resource_id: str, 
                attestation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Attestation]: ...

        @overload
        def begin_create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                attestation_name: str, 
                parameters: Attestation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Attestation]: ...

        @overload
        def begin_create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                attestation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Attestation]: ...

        @overload
        def begin_create_or_update_at_subscription(
                self, 
                attestation_name: str, 
                parameters: Attestation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Attestation]: ...

        @overload
        def begin_create_or_update_at_subscription(
                self, 
                attestation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Attestation]: ...

        @distributed_trace
        def delete_at_resource(
                self, 
                resource_id: str, 
                attestation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_resource_group(
                self, 
                resource_group_name: str, 
                attestation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_subscription(
                self, 
                attestation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_at_resource(
                self, 
                resource_id: str, 
                attestation_name: str, 
                **kwargs: Any
            ) -> Attestation: ...

        @distributed_trace
        def get_at_resource_group(
                self, 
                resource_group_name: str, 
                attestation_name: str, 
                **kwargs: Any
            ) -> Attestation: ...

        @distributed_trace
        def get_at_subscription(
                self, 
                attestation_name: str, 
                **kwargs: Any
            ) -> Attestation: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[Attestation]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[Attestation]: ...

        @distributed_trace
        def list_for_subscription(
                self, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[Attestation]: ...


    class azure.mgmt.policyinsights.operations.ComponentPolicyStatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_query_results_for_policy_definition(
                self, 
                subscription_id: str, 
                policy_definition_name: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...

        @distributed_trace
        def list_query_results_for_resource(
                self, 
                resource_id: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...

        @distributed_trace
        def list_query_results_for_resource_group(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...

        @distributed_trace
        def list_query_results_for_resource_group_level_policy_assignment(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                policy_assignment_name: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...

        @distributed_trace
        def list_query_results_for_subscription(
                self, 
                subscription_id: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...

        @distributed_trace
        def list_query_results_for_subscription_level_policy_assignment(
                self, 
                subscription_id: str, 
                policy_assignment_name: str, 
                component_policy_states_resource: Union[str, ComponentPolicyStatesResource], 
                top: Optional[int] = None, 
                order_by: Optional[str] = None, 
                select: Optional[str] = None, 
                from_parameter: Optional[datetime] = None, 
                to: Optional[datetime] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                **kwargs: Any
            ) -> ComponentPolicyStatesQueryResults: ...


    class azure.mgmt.policyinsights.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> OperationsListResults: ...


    class azure.mgmt.policyinsights.operations.PolicyEventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_query_results_for_management_group(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                management_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_policy_definition(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                policy_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_policy_set_definition(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                policy_set_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_resource(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                resource_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_resource_group(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                resource_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_resource_group_level_policy_assignment(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                resource_group_name: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_subscription(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyEvent]: ...

        @distributed_trace
        def list_query_results_for_subscription_level_policy_assignment(
                self, 
                policy_events_resource: Union[str, PolicyEventsResourceType], 
                subscription_id: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyEvent]: ...


    class azure.mgmt.policyinsights.operations.PolicyMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_resource(
                self, 
                resource_name: str, 
                **kwargs: Any
            ) -> PolicyMetadata: ...

        @distributed_trace
        def list(
                self, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[SlimPolicyMetadata]: ...


    class azure.mgmt.policyinsights.operations.PolicyRestrictionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_at_management_group_scope(
                self, 
                management_group_id: str, 
                parameters: CheckManagementGroupRestrictionsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...

        @overload
        def check_at_management_group_scope(
                self, 
                management_group_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...

        @overload
        def check_at_resource_group_scope(
                self, 
                resource_group_name: str, 
                parameters: CheckRestrictionsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...

        @overload
        def check_at_resource_group_scope(
                self, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...

        @overload
        def check_at_subscription_scope(
                self, 
                parameters: CheckRestrictionsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...

        @overload
        def check_at_subscription_scope(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckRestrictionsResult: ...


    class azure.mgmt.policyinsights.operations.PolicyStatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_trigger_resource_group_evaluation(
                self, 
                subscription_id: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_trigger_subscription_evaluation(
                self, 
                subscription_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def list_query_results_for_management_group(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                management_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_policy_definition(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                policy_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_policy_set_definition(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                policy_set_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_resource(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                resource_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_resource_group(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                resource_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_resource_group_level_policy_assignment(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                resource_group_name: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_subscription(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyState]: ...

        @distributed_trace
        def list_query_results_for_subscription_level_policy_assignment(
                self, 
                policy_states_resource: Union[str, PolicyStatesResource], 
                subscription_id: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyState]: ...

        @distributed_trace
        def summarize_for_management_group(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                management_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace
        def summarize_for_policy_definition(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                policy_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace
        def summarize_for_policy_set_definition(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                policy_set_definition_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace
        def summarize_for_resource(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                resource_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace
        def summarize_for_resource_group(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                resource_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace
        def summarize_for_resource_group_level_policy_assignment(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                resource_group_name: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace
        def summarize_for_subscription(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...

        @distributed_trace
        def summarize_for_subscription_level_policy_assignment(
                self, 
                policy_states_summary_resource: Union[str, PolicyStatesSummaryResourceType], 
                subscription_id: str, 
                policy_assignment_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> SummarizeResults: ...


    class azure.mgmt.policyinsights.operations.PolicyTrackedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_query_results_for_management_group(
                self, 
                management_group_name: str, 
                policy_tracked_resources_resource: Union[str, PolicyTrackedResourcesResourceType], 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyTrackedResource]: ...

        @distributed_trace
        def list_query_results_for_resource(
                self, 
                resource_id: str, 
                policy_tracked_resources_resource: Union[str, PolicyTrackedResourcesResourceType], 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyTrackedResource]: ...

        @distributed_trace
        def list_query_results_for_resource_group(
                self, 
                resource_group_name: str, 
                policy_tracked_resources_resource: Union[str, PolicyTrackedResourcesResourceType], 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyTrackedResource]: ...

        @distributed_trace
        def list_query_results_for_subscription(
                self, 
                policy_tracked_resources_resource: Union[str, PolicyTrackedResourcesResourceType], 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[PolicyTrackedResource]: ...


    class azure.mgmt.policyinsights.operations.RemediationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace
        def cancel_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace
        def cancel_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace
        def cancel_at_subscription(
                self, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                parameters: Remediation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        def create_or_update_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                parameters: Remediation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        def create_or_update_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        def create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                parameters: Remediation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        def create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        def create_or_update_at_subscription(
                self, 
                remediation_name: str, 
                parameters: Remediation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @overload
        def create_or_update_at_subscription(
                self, 
                remediation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace
        def delete_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Optional[Remediation]: ...

        @distributed_trace
        def delete_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Optional[Remediation]: ...

        @distributed_trace
        def delete_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Optional[Remediation]: ...

        @distributed_trace
        def delete_at_subscription(
                self, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Optional[Remediation]: ...

        @distributed_trace
        def get_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace
        def get_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace
        def get_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace
        def get_at_subscription(
                self, 
                remediation_name: str, 
                **kwargs: Any
            ) -> Remediation: ...

        @distributed_trace
        def list_deployments_at_management_group(
                self, 
                management_group_id: str, 
                remediation_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[RemediationDeployment]: ...

        @distributed_trace
        def list_deployments_at_resource(
                self, 
                resource_id: str, 
                remediation_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[RemediationDeployment]: ...

        @distributed_trace
        def list_deployments_at_resource_group(
                self, 
                resource_group_name: str, 
                remediation_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[RemediationDeployment]: ...

        @distributed_trace
        def list_deployments_at_subscription(
                self, 
                remediation_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[RemediationDeployment]: ...

        @distributed_trace
        def list_for_management_group(
                self, 
                management_group_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[Remediation]: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_id: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[Remediation]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[Remediation]: ...

        @distributed_trace
        def list_for_subscription(
                self, 
                query_options: Optional[QueryOptions] = None, 
                **kwargs: Any
            ) -> ItemPaged[Remediation]: ...


```