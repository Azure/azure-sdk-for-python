```py
namespace azure.mgmt.resource.policy

    class azure.mgmt.resource.policy.PolicyClient: implements ContextManager 
        data_policy_manifests: DataPolicyManifestsOperations
        policy_assignments: PolicyAssignmentsOperations
        policy_definition_versions: PolicyDefinitionVersionsOperations
        policy_definitions: PolicyDefinitionsOperations
        policy_enrollments: PolicyEnrollmentsOperations
        policy_exemptions: PolicyExemptionsOperations
        policy_set_definition_versions: PolicySetDefinitionVersionsOperations
        policy_set_definitions: PolicySetDefinitionsOperations
        policy_tokens: PolicyTokensOperations
        variable_values: VariableValuesOperations
        variables: VariablesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.resource.policy.aio

    class azure.mgmt.resource.policy.aio.PolicyClient: implements AsyncContextManager 
        data_policy_manifests: DataPolicyManifestsOperations
        policy_assignments: PolicyAssignmentsOperations
        policy_definition_versions: PolicyDefinitionVersionsOperations
        policy_definitions: PolicyDefinitionsOperations
        policy_enrollments: PolicyEnrollmentsOperations
        policy_exemptions: PolicyExemptionsOperations
        policy_set_definition_versions: PolicySetDefinitionVersionsOperations
        policy_set_definitions: PolicySetDefinitionsOperations
        policy_tokens: PolicyTokensOperations
        variable_values: VariableValuesOperations
        variables: VariablesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.resource.policy.aio.operations

    class azure.mgmt.resource.policy.aio.operations.DataPolicyManifestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'policy_mode', 'accept']}, api_versions_list=['2025-11-01', '2025-12-01-preview', '2026-01-01-preview'])
        async def get_by_policy_mode(
                self, 
                policy_mode: str, 
                **kwargs: Any
            ) -> DataPolicyManifest: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'filter', 'accept']}, api_versions_list=['2025-11-01', '2025-12-01-preview', '2026-01-01-preview'])
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DataPolicyManifest]: ...


    class azure.mgmt.resource.policy.aio.operations.PolicyAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def create(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def create(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def create_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def create_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def create_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[PolicyAssignment]: ...

        @distributed_trace_async
        async def delete_by_id(
                self, 
                policy_assignment_id: str, 
                **kwargs: Any
            ) -> Optional[PolicyAssignment]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                policy_assignment_id: str, 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_management_group(
                self, 
                management_group_id: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyAssignment]: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def update_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def update_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        async def update_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...


    class azure.mgmt.resource.policy.aio.operations.PolicyDefinitionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        async def create_or_update(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        async def create_or_update(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace_async
        async def get_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace_async
        async def get_built_in(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace
        def list(
                self, 
                policy_definition_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinitionVersion]: ...

        @distributed_trace_async
        async def list_all(self, **kwargs: Any) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace_async
        async def list_all_at_management_group(
                self, 
                management_group_name: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace_async
        async def list_all_builtins(self, **kwargs: Any) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace
        def list_built_in(
                self, 
                policy_definition_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinitionVersion]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinitionVersion]: ...


    class azure.mgmt.resource.policy.aio.operations.PolicyDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        async def create_or_update(
                self, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        async def create_or_update(
                self, 
                policy_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace_async
        async def delete(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace_async
        async def get_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace_async
        async def get_built_in(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinition]: ...

        @distributed_trace
        def list_built_in(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinition]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyDefinition]: ...


    class azure.mgmt.resource.policy.aio.operations.PolicyEnrollmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: PolicyEnrollment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: PolicyEnrollment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'scope', 'policy_enrollment_name']}, api_versions_list=['2026-01-01-preview'])
        async def delete(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'scope', 'policy_enrollment_name', 'accept']}, api_versions_list=['2026-01-01-preview'])
        async def get(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'filter', 'accept']}, api_versions_list=['2026-01-01-preview'])
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEnrollment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'management_group_id', 'filter', 'accept']}, api_versions_list=['2026-01-01-preview'])
        def list_for_management_group(
                self, 
                management_group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEnrollment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['subscription_id', 'resource_group_name', 'resource_provider_namespace', 'parent_resource_path', 'resource_type', 'resource_name', 'api_version', 'filter', 'accept']}, api_versions_list=['2026-01-01-preview'])
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
            ) -> AsyncItemPaged[PolicyEnrollment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'filter', 'accept']}, api_versions_list=['2026-01-01-preview'])
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyEnrollment]: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: PolicyEnrollmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: PolicyEnrollmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...


    class azure.mgmt.resource.policy.aio.operations.PolicyExemptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: PolicyExemption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: PolicyExemption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'scope', 'policy_exemption_name']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        async def delete(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'scope', 'policy_exemption_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        async def get(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'filter', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyExemption]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'filter', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list_for_management_group(
                self, 
                management_group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyExemption]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['subscription_id', 'resource_group_name', 'resource_provider_namespace', 'parent_resource_path', 'resource_type', 'resource_name', 'api_version', 'filter', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
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
            ) -> AsyncItemPaged[PolicyExemption]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'filter', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyExemption]: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: PolicyExemptionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: PolicyExemptionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @overload
        async def update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...


    class azure.mgmt.resource.policy.aio.operations.PolicySetDefinitionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        async def create_or_update(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        async def create_or_update(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace_async
        async def get_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace_async
        async def get_built_in(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace
        def list(
                self, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinitionVersion]: ...

        @distributed_trace_async
        async def list_all(self, **kwargs: Any) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace_async
        async def list_all_at_management_group(
                self, 
                management_group_name: str, 
                **kwargs: Any
            ) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace_async
        async def list_all_builtins(self, **kwargs: Any) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace
        def list_built_in(
                self, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinitionVersion]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinitionVersion]: ...


    class azure.mgmt.resource.policy.aio.operations.PolicySetDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        async def create_or_update(
                self, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        async def create_or_update(
                self, 
                policy_set_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace_async
        async def delete(
                self, 
                policy_set_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace_async
        async def get_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace_async
        async def get_built_in(
                self, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinition]: ...

        @distributed_trace
        def list_built_in(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinition]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_id: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicySetDefinition]: ...


    class azure.mgmt.resource.policy.aio.operations.PolicyTokensOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def acquire(
                self, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        async def acquire(
                self, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        async def acquire(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        async def acquire_at_management_group(
                self, 
                management_group_name: str, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        async def acquire_at_management_group(
                self, 
                management_group_name: str, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        async def acquire_at_management_group(
                self, 
                management_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...


    class azure.mgmt.resource.policy.aio.operations.VariableValuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: VariableValue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @overload
        async def create_or_update(
                self, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: VariableValue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @overload
        async def create_or_update(
                self, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: VariableValue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: VariableValue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'variable_name', 'variable_value_name']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        async def delete(
                self, 
                variable_name: str, 
                variable_value_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'variable_name', 'variable_value_name']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        async def delete_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                variable_value_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'variable_name', 'variable_value_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        async def get(
                self, 
                variable_name: str, 
                variable_value_name: str, 
                **kwargs: Any
            ) -> VariableValue: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'variable_name', 'variable_value_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        async def get_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                variable_value_name: str, 
                **kwargs: Any
            ) -> VariableValue: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'variable_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list(
                self, 
                variable_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VariableValue]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'variable_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list_for_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VariableValue]: ...


    class azure.mgmt.resource.policy.aio.operations.VariablesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                variable_name: str, 
                parameters: Variable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        async def create_or_update(
                self, 
                variable_name: str, 
                parameters: Variable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        async def create_or_update(
                self, 
                variable_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                parameters: Variable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                parameters: Variable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        async def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'variable_name']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        async def delete(
                self, 
                variable_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'variable_name']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        async def delete_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'variable_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        async def get(
                self, 
                variable_name: str, 
                **kwargs: Any
            ) -> Variable: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'variable_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        async def get_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                **kwargs: Any
            ) -> Variable: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list(self, **kwargs: Any) -> AsyncItemPaged[Variable]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list_for_management_group(
                self, 
                management_group_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Variable]: ...


namespace azure.mgmt.resource.policy.models

    class azure.mgmt.resource.policy.models.Alias(_Model):
        default_metadata: Optional[AliasPathMetadata]
        default_path: Optional[str]
        default_pattern: Optional[AliasPattern]
        name: Optional[str]
        paths: Optional[list[AliasPath]]
        type: Optional[Union[str, AliasType]]

        @overload
        def __init__(
                self, 
                *, 
                default_metadata: Optional[AliasPathMetadata] = ..., 
                default_path: Optional[str] = ..., 
                default_pattern: Optional[AliasPattern] = ..., 
                name: Optional[str] = ..., 
                paths: Optional[list[AliasPath]] = ..., 
                type: Optional[Union[str, AliasType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.AliasPath(_Model):
        api_versions: Optional[list[str]]
        metadata: Optional[AliasPathMetadata]
        path: Optional[str]
        pattern: Optional[AliasPattern]

        @overload
        def __init__(
                self, 
                *, 
                api_versions: Optional[list[str]] = ..., 
                path: Optional[str] = ..., 
                pattern: Optional[AliasPattern] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.AliasPathAttributes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MODIFIABLE = "Modifiable"
        NONE = "None"


    class azure.mgmt.resource.policy.models.AliasPathMetadata(_Model):
        attributes: Optional[Union[str, AliasPathAttributes]]
        type: Optional[Union[str, AliasPathTokenType]]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[Union[str, AliasPathAttributes]] = ..., 
                type: Optional[Union[str, AliasPathTokenType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.AliasPathTokenType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        ARRAY = "Array"
        BOOLEAN = "Boolean"
        INTEGER = "Integer"
        NOT_SPECIFIED = "NotSpecified"
        NUMBER = "Number"
        OBJECT = "Object"
        STRING = "String"


    class azure.mgmt.resource.policy.models.AliasPattern(_Model):
        phrase: Optional[str]
        type: Optional[Union[str, AliasPatternType]]
        variable: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                phrase: Optional[str] = ..., 
                type: Optional[Union[str, AliasPatternType]] = ..., 
                variable: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.AliasPatternType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTRACT = "Extract"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.resource.policy.models.AliasType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MASK = "Mask"
        NOT_SPECIFIED = "NotSpecified"
        PLAIN_TEXT = "PlainText"


    class azure.mgmt.resource.policy.models.AssignmentScopeValidation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        DO_NOT_VALIDATE = "DoNotValidate"


    class azure.mgmt.resource.policy.models.AssignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        NOT_SPECIFIED = "NotSpecified"
        SYSTEM = "System"
        SYSTEM_HIDDEN = "SystemHidden"


    class azure.mgmt.resource.policy.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resource.policy.models.DataEffect(_Model):
        details_schema: Optional[Any]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                details_schema: Optional[Any] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.DataManifestCustomResourceFunctionDefinition(_Model):
        allow_custom_properties: Optional[bool]
        default_properties: Optional[list[str]]
        fully_qualified_resource_type: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allow_custom_properties: Optional[bool] = ..., 
                default_properties: Optional[list[str]] = ..., 
                fully_qualified_resource_type: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.DataManifestResourceFunctionsDefinition(_Model):
        custom: Optional[list[DataManifestCustomResourceFunctionDefinition]]
        standard: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                custom: Optional[list[DataManifestCustomResourceFunctionDefinition]] = ..., 
                standard: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.DataPolicyManifest(ProxyResource):
        id: str
        name: str
        properties: Optional[DataPolicyManifestProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DataPolicyManifestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.DataPolicyManifestProperties(_Model):
        effects: Optional[list[DataEffect]]
        field_values: Optional[list[str]]
        is_built_in_only: Optional[bool]
        namespaces: Optional[list[str]]
        policy_mode: Optional[str]
        resource_functions: Optional[DataManifestResourceFunctionsDefinition]
        resource_type_aliases: Optional[list[ResourceTypeAliases]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                effects: Optional[list[DataEffect]] = ..., 
                field_values: Optional[list[str]] = ..., 
                is_built_in_only: Optional[bool] = ..., 
                namespaces: Optional[list[str]] = ..., 
                policy_mode: Optional[str] = ..., 
                resource_functions: Optional[DataManifestResourceFunctionsDefinition] = ..., 
                resource_type_aliases: Optional[list[ResourceTypeAliases]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.EnforcementMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        DO_NOT_ENFORCE = "DoNotEnforce"
        ENROLL = "Enroll"


    class azure.mgmt.resource.policy.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.resource.policy.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.resource.policy.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.ExemptionCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MITIGATED = "Mitigated"
        WAIVER = "Waiver"


    class azure.mgmt.resource.policy.models.ExemptionManagementMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN = "Admin"
        USER_SELF_SERVE = "UserSelfServe"


    class azure.mgmt.resource.policy.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resource.policy.models.ExternalEndpointResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.resource.policy.models.ExternalEvaluationEndpointInvocationResult(_Model):
        additional_info: Optional[Any]
        claims: Optional[Any]
        endpoint_kind: Optional[str]
        expiration: Optional[datetime]
        message: Optional[str]
        policy_action: Optional[Union[str, PolicyAction]]
        policy_evaluation_details: Optional[Any]
        policy_info: Optional[PolicyLogInfo]
        result: Optional[Union[str, ExternalEndpointResult]]
        retry_after: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[Any] = ..., 
                claims: Optional[Any] = ..., 
                endpoint_kind: Optional[str] = ..., 
                expiration: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                policy_action: Optional[Union[str, PolicyAction]] = ..., 
                policy_evaluation_details: Optional[Any] = ..., 
                policy_info: Optional[PolicyLogInfo] = ..., 
                result: Optional[Union[str, ExternalEndpointResult]] = ..., 
                retry_after: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.ExternalEvaluationEndpointSettings(_Model):
        details: Optional[Any]
        kind: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[Any] = ..., 
                kind: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.ExternalEvaluationEnforcementSettings(_Model):
        endpoint_settings: Optional[ExternalEvaluationEndpointSettings]
        missing_token_action: Optional[str]
        result_lifespan: Optional[str]
        role_definition_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_settings: Optional[ExternalEvaluationEndpointSettings] = ..., 
                missing_token_action: Optional[str] = ..., 
                result_lifespan: Optional[str] = ..., 
                role_definition_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.NonComplianceMessage(_Model):
        message: str
        policy_definition_reference_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: str, 
                policy_definition_reference_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.Override(_Model):
        kind: Optional[Union[str, OverrideKind]]
        selectors: Optional[list[Selector]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, OverrideKind]] = ..., 
                selectors: Optional[list[Selector]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.OverrideKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFINITION_VERSION = "definitionVersion"
        POLICY_EFFECT = "policyEffect"


    class azure.mgmt.resource.policy.models.ParameterDefinitionsValue(_Model):
        allowed_values: Optional[list[Any]]
        default_value: Optional[Any]
        metadata: Optional[ParameterDefinitionsValueMetadata]
        schema: Optional[Any]
        type: Optional[Union[str, ParameterType]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_values: Optional[list[Any]] = ..., 
                default_value: Optional[Any] = ..., 
                metadata: Optional[ParameterDefinitionsValueMetadata] = ..., 
                schema: Optional[Any] = ..., 
                type: Optional[Union[str, ParameterType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.ParameterDefinitionsValueMetadata(_Model):
        assign_permissions: Optional[bool]
        description: Optional[str]
        display_name: Optional[str]
        strong_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assign_permissions: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                strong_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.ParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "Array"
        BOOLEAN = "Boolean"
        DATE_TIME = "DateTime"
        FLOAT = "Float"
        INTEGER = "Integer"
        OBJECT = "Object"
        STRING = "String"


    class azure.mgmt.resource.policy.models.ParameterValuesValue(_Model):
        value: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        AUDIT = "Audit"
        DENY = "Deny"
        ERROR = "Error"
        UNKNOWN = "Unknown"


    class azure.mgmt.resource.policy.models.PolicyAssignment(ExtensionResource):
        id: str
        identity: Optional[Identity]
        location: Optional[str]
        name: str
        properties: Optional[PolicyAssignmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[PolicyAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyAssignmentProperties(_Model):
        assignment_type: Optional[Union[str, AssignmentType]]
        definition_version: Optional[str]
        description: Optional[str]
        display_name: Optional[str]
        effective_definition_version: Optional[str]
        enforcement_mode: Optional[Union[str, EnforcementMode]]
        instance_id: Optional[str]
        latest_definition_version: Optional[str]
        metadata: Optional[Any]
        non_compliance_messages: Optional[list[NonComplianceMessage]]
        not_scopes: Optional[list[str]]
        overrides: Optional[list[Override]]
        parameters: Optional[dict[str, ParameterValuesValue]]
        policy_definition_id: Optional[str]
        resource_selectors: Optional[list[ResourceSelector]]
        scope: Optional[str]
        self_serve_exemption_settings: Optional[SelfServeExemptionSettings]

        @overload
        def __init__(
                self, 
                *, 
                assignment_type: Optional[Union[str, AssignmentType]] = ..., 
                definition_version: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enforcement_mode: Optional[Union[str, EnforcementMode]] = ..., 
                metadata: Optional[Any] = ..., 
                non_compliance_messages: Optional[list[NonComplianceMessage]] = ..., 
                not_scopes: Optional[list[str]] = ..., 
                overrides: Optional[list[Override]] = ..., 
                parameters: Optional[dict[str, ParameterValuesValue]] = ..., 
                policy_definition_id: Optional[str] = ..., 
                resource_selectors: Optional[list[ResourceSelector]] = ..., 
                self_serve_exemption_settings: Optional[SelfServeExemptionSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyAssignmentUpdate(_Model):
        identity: Optional[Identity]
        location: Optional[str]
        properties: Optional[PolicyAssignmentUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[PolicyAssignmentUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyAssignmentUpdateProperties(_Model):
        overrides: Optional[list[Override]]
        resource_selectors: Optional[list[ResourceSelector]]
        self_serve_exemption_settings: Optional[SelfServeExemptionSettings]

        @overload
        def __init__(
                self, 
                *, 
                overrides: Optional[list[Override]] = ..., 
                resource_selectors: Optional[list[ResourceSelector]] = ..., 
                self_serve_exemption_settings: Optional[SelfServeExemptionSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[PolicyDefinitionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicyDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyDefinitionGroup(_Model):
        additional_metadata_id: Optional[str]
        category: Optional[str]
        description: Optional[str]
        display_name: Optional[str]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                additional_metadata_id: Optional[str] = ..., 
                category: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyDefinitionProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        external_evaluation_enforcement_settings: Optional[ExternalEvaluationEnforcementSettings]
        metadata: Optional[Any]
        mode: Optional[str]
        parameters: Optional[dict[str, ParameterDefinitionsValue]]
        policy_rule: Optional[Any]
        policy_type: Optional[Union[str, PolicyType]]
        version: Optional[str]
        versions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                external_evaluation_enforcement_settings: Optional[ExternalEvaluationEnforcementSettings] = ..., 
                metadata: Optional[Any] = ..., 
                mode: Optional[str] = ..., 
                parameters: Optional[dict[str, ParameterDefinitionsValue]] = ..., 
                policy_rule: Optional[Any] = ..., 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
                version: Optional[str] = ..., 
                versions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyDefinitionReference(_Model):
        definition_version: Optional[str]
        effective_definition_version: Optional[str]
        group_names: Optional[list[str]]
        latest_definition_version: Optional[str]
        parameters: Optional[dict[str, ParameterValuesValue]]
        policy_definition_id: str
        policy_definition_reference_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                definition_version: Optional[str] = ..., 
                group_names: Optional[list[str]] = ..., 
                parameters: Optional[dict[str, ParameterValuesValue]] = ..., 
                policy_definition_id: str, 
                policy_definition_reference_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyDefinitionVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[PolicyDefinitionVersionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicyDefinitionVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyDefinitionVersionListResult(_Model):
        next_link: Optional[str]
        value: list[PolicyDefinitionVersion]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PolicyDefinitionVersion]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyDefinitionVersionProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        external_evaluation_enforcement_settings: Optional[ExternalEvaluationEnforcementSettings]
        metadata: Optional[Any]
        mode: Optional[str]
        parameters: Optional[dict[str, ParameterDefinitionsValue]]
        policy_rule: Optional[Any]
        policy_type: Optional[Union[str, PolicyType]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                external_evaluation_enforcement_settings: Optional[ExternalEvaluationEnforcementSettings] = ..., 
                metadata: Optional[Any] = ..., 
                mode: Optional[str] = ..., 
                parameters: Optional[dict[str, ParameterDefinitionsValue]] = ..., 
                policy_rule: Optional[Any] = ..., 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyEnrollment(ExtensionResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[PolicyEnrollmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                properties: Optional[PolicyEnrollmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyEnrollmentProperties(_Model):
        assignment_scope_validation: Optional[Union[str, AssignmentScopeValidation]]
        description: Optional[str]
        display_name: Optional[str]
        metadata: Optional[Any]
        policy_assignment_id: str
        policy_assignment_instance_id: Optional[str]
        policy_definition_reference_ids: Optional[list[str]]
        resource_selectors: Optional[list[ResourceSelector]]

        @overload
        def __init__(
                self, 
                *, 
                assignment_scope_validation: Optional[Union[str, AssignmentScopeValidation]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                metadata: Optional[Any] = ..., 
                policy_assignment_id: str, 
                policy_definition_reference_ids: Optional[list[str]] = ..., 
                resource_selectors: Optional[list[ResourceSelector]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyEnrollmentUpdate(_Model):
        properties: Optional[PolicyEnrollmentUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicyEnrollmentUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyEnrollmentUpdateProperties(_Model):
        assignment_scope_validation: Optional[Union[str, AssignmentScopeValidation]]
        resource_selectors: Optional[list[ResourceSelector]]

        @overload
        def __init__(
                self, 
                *, 
                assignment_scope_validation: Optional[Union[str, AssignmentScopeValidation]] = ..., 
                resource_selectors: Optional[list[ResourceSelector]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyExemption(ExtensionResource):
        id: str
        name: str
        properties: Optional[PolicyExemptionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicyExemptionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyExemptionProperties(_Model):
        assignment_scope_validation: Optional[Union[str, AssignmentScopeValidation]]
        description: Optional[str]
        display_name: Optional[str]
        exemption_category: Union[str, ExemptionCategory]
        exemption_management_mode: Optional[Union[str, ExemptionManagementMode]]
        expires_on: Optional[datetime]
        metadata: Optional[Any]
        policy_assignment_id: str
        policy_definition_reference_ids: Optional[list[str]]
        resource_selectors: Optional[list[ResourceSelector]]

        @overload
        def __init__(
                self, 
                *, 
                assignment_scope_validation: Optional[Union[str, AssignmentScopeValidation]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                exemption_category: Union[str, ExemptionCategory], 
                exemption_management_mode: Optional[Union[str, ExemptionManagementMode]] = ..., 
                expires_on: Optional[datetime] = ..., 
                metadata: Optional[Any] = ..., 
                policy_assignment_id: str, 
                policy_definition_reference_ids: Optional[list[str]] = ..., 
                resource_selectors: Optional[list[ResourceSelector]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyExemptionUpdate(_Model):
        properties: Optional[PolicyExemptionUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicyExemptionUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyExemptionUpdateProperties(_Model):
        assignment_scope_validation: Optional[Union[str, AssignmentScopeValidation]]
        exemption_management_mode: Optional[Union[str, ExemptionManagementMode]]
        resource_selectors: Optional[list[ResourceSelector]]

        @overload
        def __init__(
                self, 
                *, 
                assignment_scope_validation: Optional[Union[str, AssignmentScopeValidation]] = ..., 
                exemption_management_mode: Optional[Union[str, ExemptionManagementMode]] = ..., 
                resource_selectors: Optional[list[ResourceSelector]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyLogInfo(_Model):
        policy_assignment_id: Optional[str]
        policy_assignment_name: Optional[str]
        policy_assignment_scope: Optional[str]
        policy_assignment_version: Optional[str]
        policy_definition_effect: Optional[str]
        policy_definition_id: Optional[str]
        policy_definition_name: Optional[str]
        policy_definition_reference_id: Optional[str]
        policy_definition_version: Optional[str]
        policy_set_definition_id: Optional[str]
        policy_set_definition_name: Optional[str]
        policy_set_definition_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                policy_assignment_id: Optional[str] = ..., 
                policy_assignment_name: Optional[str] = ..., 
                policy_assignment_scope: Optional[str] = ..., 
                policy_assignment_version: Optional[str] = ..., 
                policy_definition_effect: Optional[str] = ..., 
                policy_definition_id: Optional[str] = ..., 
                policy_definition_name: Optional[str] = ..., 
                policy_definition_reference_id: Optional[str] = ..., 
                policy_definition_version: Optional[str] = ..., 
                policy_set_definition_id: Optional[str] = ..., 
                policy_set_definition_name: Optional[str] = ..., 
                policy_set_definition_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicySetDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[PolicySetDefinitionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicySetDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.PolicySetDefinitionProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        metadata: Optional[Any]
        parameters: Optional[dict[str, ParameterDefinitionsValue]]
        policy_definition_groups: Optional[list[PolicyDefinitionGroup]]
        policy_definitions: list[PolicyDefinitionReference]
        policy_type: Optional[Union[str, PolicyType]]
        version: Optional[str]
        versions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                metadata: Optional[Any] = ..., 
                parameters: Optional[dict[str, ParameterDefinitionsValue]] = ..., 
                policy_definition_groups: Optional[list[PolicyDefinitionGroup]] = ..., 
                policy_definitions: list[PolicyDefinitionReference], 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
                version: Optional[str] = ..., 
                versions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicySetDefinitionVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[PolicySetDefinitionVersionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicySetDefinitionVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.PolicySetDefinitionVersionListResult(_Model):
        next_link: Optional[str]
        value: list[PolicySetDefinitionVersion]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PolicySetDefinitionVersion]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicySetDefinitionVersionProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        metadata: Optional[Any]
        parameters: Optional[dict[str, ParameterDefinitionsValue]]
        policy_definition_groups: Optional[list[PolicyDefinitionGroup]]
        policy_definitions: list[PolicyDefinitionReference]
        policy_type: Optional[Union[str, PolicyType]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                metadata: Optional[Any] = ..., 
                parameters: Optional[dict[str, ParameterDefinitionsValue]] = ..., 
                policy_definition_groups: Optional[list[PolicyDefinitionGroup]] = ..., 
                policy_definitions: list[PolicyDefinitionReference], 
                policy_type: Optional[Union[str, PolicyType]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyTokenEvaluatedRequestDetails(_Model):
        api_version: str
        authorization_action: str
        content_hash: str
        http_method: str
        resource_id: str
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                api_version: str, 
                authorization_action: str, 
                content_hash: str, 
                http_method: str, 
                resource_id: str, 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyTokenOperation(_Model):
        content: Optional[Any]
        http_method: str
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[Any] = ..., 
                http_method: str, 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyTokenRequest(_Model):
        change_reference: Optional[str]
        operation: PolicyTokenOperation

        @overload
        def __init__(
                self, 
                *, 
                change_reference: Optional[str] = ..., 
                operation: PolicyTokenOperation
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyTokenResponse(_Model):
        change_reference: Optional[str]
        expiration: Optional[datetime]
        message: Optional[str]
        request_details: Optional[PolicyTokenEvaluatedRequestDetails]
        result: Optional[Union[str, PolicyTokenResult]]
        results: Optional[list[ExternalEvaluationEndpointInvocationResult]]
        retry_after: Optional[datetime]
        token: Optional[str]
        token_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                change_reference: Optional[str] = ..., 
                expiration: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                request_details: Optional[PolicyTokenEvaluatedRequestDetails] = ..., 
                result: Optional[Union[str, PolicyTokenResult]] = ..., 
                results: Optional[list[ExternalEvaluationEndpointInvocationResult]] = ..., 
                retry_after: Optional[datetime] = ..., 
                token: Optional[str] = ..., 
                token_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyTokenResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.resource.policy.models.PolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN = "BuiltIn"
        CUSTOM = "Custom"
        NOT_SPECIFIED = "NotSpecified"
        STATIC = "Static"


    class azure.mgmt.resource.policy.models.PolicyVariableColumn(_Model):
        column_name: str

        @overload
        def __init__(
                self, 
                *, 
                column_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyVariableProperties(_Model):
        columns: list[PolicyVariableColumn]

        @overload
        def __init__(
                self, 
                *, 
                columns: list[PolicyVariableColumn]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyVariableValueColumnValue(_Model):
        column_name: str
        column_value: Any

        @overload
        def __init__(
                self, 
                *, 
                column_name: str, 
                column_value: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.PolicyVariableValueProperties(_Model):
        values_property: list[PolicyVariableValueColumnValue]

        @overload
        def __init__(
                self, 
                *, 
                values_property: list[PolicyVariableValueColumnValue]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resource.policy.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.resource.policy.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.resource.policy.models.ResourceSelector(_Model):
        name: Optional[str]
        selectors: Optional[list[Selector]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                selectors: Optional[list[Selector]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.ResourceTypeAliases(_Model):
        aliases: Optional[list[Alias]]
        resource_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aliases: Optional[list[Alias]] = ..., 
                resource_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.Selector(_Model):
        in_property: Optional[list[str]]
        kind: Optional[Union[str, SelectorKind]]
        not_in: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                in_property: Optional[list[str]] = ..., 
                kind: Optional[Union[str, SelectorKind]] = ..., 
                not_in: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.SelectorKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP_PRINCIPAL_ID = "groupPrincipalId"
        POLICY_DEFINITION_REFERENCE_ID = "policyDefinitionReferenceId"
        RESOURCE_LOCATION = "resourceLocation"
        RESOURCE_TYPE = "resourceType"
        RESOURCE_WITHOUT_LOCATION = "resourceWithoutLocation"
        USER_PRINCIPAL_ID = "userPrincipalId"


    class azure.mgmt.resource.policy.models.SelfServeExemptionSettings(_Model):
        enabled: Optional[bool]
        policy_definition_reference_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                policy_definition_reference_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.policy.models.SystemData(_Model):
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


    class azure.mgmt.resource.policy.models.UserAssignedIdentitiesValue(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.resource.policy.models.Variable(ProxyResource):
        id: str
        name: str
        properties: Optional[PolicyVariableProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicyVariableProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.policy.models.VariableValue(ProxyResource):
        id: str
        name: str
        properties: Optional[PolicyVariableValueProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicyVariableValueProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


namespace azure.mgmt.resource.policy.operations

    class azure.mgmt.resource.policy.operations.DataPolicyManifestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'policy_mode', 'accept']}, api_versions_list=['2025-11-01', '2025-12-01-preview', '2026-01-01-preview'])
        def get_by_policy_mode(
                self, 
                policy_mode: str, 
                **kwargs: Any
            ) -> DataPolicyManifest: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'filter', 'accept']}, api_versions_list=['2025-11-01', '2025-12-01-preview', '2026-01-01-preview'])
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DataPolicyManifest]: ...


    class azure.mgmt.resource.policy.operations.PolicyAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def create(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def create(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def create_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def create_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def create_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[PolicyAssignment]: ...

        @distributed_trace
        def delete_by_id(
                self, 
                policy_assignment_id: str, 
                **kwargs: Any
            ) -> Optional[PolicyAssignment]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace
        def get_by_id(
                self, 
                policy_assignment_id: str, 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_management_group(
                self, 
                management_group_id: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_resource(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyAssignment]: ...

        @distributed_trace
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyAssignment]: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def update_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def update_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: PolicyAssignmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...

        @overload
        def update_by_id(
                self, 
                policy_assignment_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyAssignment: ...


    class azure.mgmt.resource.policy.operations.PolicyDefinitionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        def create_or_update(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        def create_or_update(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicyDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace
        def delete(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace
        def get_at_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace
        def get_built_in(
                self, 
                policy_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersion: ...

        @distributed_trace
        def list(
                self, 
                policy_definition_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinitionVersion]: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace
        def list_all_at_management_group(
                self, 
                management_group_name: str, 
                **kwargs: Any
            ) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace
        def list_all_builtins(self, **kwargs: Any) -> PolicyDefinitionVersionListResult: ...

        @distributed_trace
        def list_built_in(
                self, 
                policy_definition_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinitionVersion]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_name: str, 
                policy_definition_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinitionVersion]: ...


    class azure.mgmt.resource.policy.operations.PolicyDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        def create_or_update(
                self, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        def create_or_update(
                self, 
                policy_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                parameters: PolicyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace
        def delete(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace
        def get_at_management_group(
                self, 
                management_group_id: str, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace
        def get_built_in(
                self, 
                policy_definition_name: str, 
                **kwargs: Any
            ) -> PolicyDefinition: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinition]: ...

        @distributed_trace
        def list_built_in(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinition]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyDefinition]: ...


    class azure.mgmt.resource.policy.operations.PolicyEnrollmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: PolicyEnrollment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: PolicyEnrollment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'scope', 'policy_enrollment_name']}, api_versions_list=['2026-01-01-preview'])
        def delete(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'scope', 'policy_enrollment_name', 'accept']}, api_versions_list=['2026-01-01-preview'])
        def get(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'filter', 'accept']}, api_versions_list=['2026-01-01-preview'])
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyEnrollment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'management_group_id', 'filter', 'accept']}, api_versions_list=['2026-01-01-preview'])
        def list_for_management_group(
                self, 
                management_group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyEnrollment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['subscription_id', 'resource_group_name', 'resource_provider_namespace', 'parent_resource_path', 'resource_type', 'resource_name', 'api_version', 'filter', 'accept']}, api_versions_list=['2026-01-01-preview'])
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
            ) -> ItemPaged[PolicyEnrollment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'filter', 'accept']}, api_versions_list=['2026-01-01-preview'])
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyEnrollment]: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: PolicyEnrollmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: PolicyEnrollmentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_enrollment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyEnrollment: ...


    class azure.mgmt.resource.policy.operations.PolicyExemptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: PolicyExemption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: PolicyExemption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'scope', 'policy_exemption_name']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def delete(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'scope', 'policy_exemption_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def get(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'filter', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyExemption]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'filter', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list_for_management_group(
                self, 
                management_group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyExemption]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['subscription_id', 'resource_group_name', 'resource_provider_namespace', 'parent_resource_path', 'resource_type', 'resource_name', 'api_version', 'filter', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
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
            ) -> ItemPaged[PolicyExemption]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'filter', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list_for_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicyExemption]: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: PolicyExemptionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: PolicyExemptionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...

        @overload
        def update(
                self, 
                scope: str, 
                policy_exemption_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyExemption: ...


    class azure.mgmt.resource.policy.operations.PolicySetDefinitionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        def create_or_update(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        def create_or_update(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: PolicySetDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace
        def delete(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace
        def get_at_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace
        def get_built_in(
                self, 
                policy_set_definition_name: str, 
                policy_definition_version: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinitionVersion: ...

        @distributed_trace
        def list(
                self, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinitionVersion]: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace
        def list_all_at_management_group(
                self, 
                management_group_name: str, 
                **kwargs: Any
            ) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace
        def list_all_builtins(self, **kwargs: Any) -> PolicySetDefinitionVersionListResult: ...

        @distributed_trace
        def list_built_in(
                self, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinitionVersion]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_name: str, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinitionVersion]: ...


    class azure.mgmt.resource.policy.operations.PolicySetDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        def create_or_update(
                self, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        def create_or_update(
                self, 
                policy_set_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                parameters: PolicySetDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace
        def delete(
                self, 
                policy_set_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace
        def get_at_management_group(
                self, 
                management_group_id: str, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace
        def get_built_in(
                self, 
                policy_set_definition_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> PolicySetDefinition: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinition]: ...

        @distributed_trace
        def list_built_in(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinition]: ...

        @distributed_trace
        def list_by_management_group(
                self, 
                management_group_id: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PolicySetDefinition]: ...


    class azure.mgmt.resource.policy.operations.PolicyTokensOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def acquire(
                self, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        def acquire(
                self, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        def acquire(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        def acquire_at_management_group(
                self, 
                management_group_name: str, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        def acquire_at_management_group(
                self, 
                management_group_name: str, 
                parameters: PolicyTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...

        @overload
        def acquire_at_management_group(
                self, 
                management_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PolicyTokenResponse: ...


    class azure.mgmt.resource.policy.operations.VariableValuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: VariableValue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @overload
        def create_or_update(
                self, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: VariableValue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @overload
        def create_or_update(
                self, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: VariableValue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: VariableValue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                variable_value_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VariableValue: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'variable_name', 'variable_value_name']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def delete(
                self, 
                variable_name: str, 
                variable_value_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'variable_name', 'variable_value_name']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def delete_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                variable_value_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'variable_name', 'variable_value_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def get(
                self, 
                variable_name: str, 
                variable_value_name: str, 
                **kwargs: Any
            ) -> VariableValue: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'variable_name', 'variable_value_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def get_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                variable_value_name: str, 
                **kwargs: Any
            ) -> VariableValue: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'variable_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list(
                self, 
                variable_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VariableValue]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'variable_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list_for_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VariableValue]: ...


    class azure.mgmt.resource.policy.operations.VariablesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                variable_name: str, 
                parameters: Variable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        def create_or_update(
                self, 
                variable_name: str, 
                parameters: Variable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        def create_or_update(
                self, 
                variable_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                parameters: Variable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                parameters: Variable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        def create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'variable_name']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def delete(
                self, 
                variable_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'variable_name']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def delete_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'variable_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def get(
                self, 
                variable_name: str, 
                **kwargs: Any
            ) -> Variable: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'variable_name', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def get_at_management_group(
                self, 
                management_group_id: str, 
                variable_name: str, 
                **kwargs: Any
            ) -> Variable: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list(self, **kwargs: Any) -> ItemPaged[Variable]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01-preview', params_added_on={'2025-12-01-preview': ['api_version', 'management_group_id', 'accept']}, api_versions_list=['2025-12-01-preview', '2026-01-01-preview'])
        def list_for_management_group(
                self, 
                management_group_id: str, 
                **kwargs: Any
            ) -> ItemPaged[Variable]: ...


namespace azure.mgmt.resource.policy.types

    class azure.mgmt.resource.policy.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.ExternalEvaluationEndpointSettings(TypedDict, total=False):
        key "details": Any
        key "kind": str
        details: Any
        kind: str


    class azure.mgmt.resource.policy.types.ExternalEvaluationEnforcementSettings(TypedDict, total=False):
        key "endpointSettings": ForwardRef('ExternalEvaluationEndpointSettings', module='types')
        key "missingTokenAction": str
        key "resultLifespan": str
        endpointSettings: ExternalEvaluationEndpointSettings
        missingTokenAction: str
        resultLifespan: str
        roleDefinitionIds: list[str]


    class azure.mgmt.resource.policy.types.Identity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        principalId: str
        tenantId: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentitiesValue]


    class azure.mgmt.resource.policy.types.NonComplianceMessage(TypedDict, total=False):
        key "message": Required[str]
        key "policyDefinitionReferenceId": str
        message: str
        policyDefinitionReferenceId: str


    class azure.mgmt.resource.policy.types.Override(TypedDict, total=False):
        key "kind": Union[str, OverrideKind]
        key "value": str
        kind: Union[str, OverrideKind]
        selectors: list[Selector]
        value: str


    class azure.mgmt.resource.policy.types.ParameterDefinitionsValue(TypedDict, total=False):
        key "defaultValue": Any
        key "metadata": ForwardRef('ParameterDefinitionsValueMetadata', module='types')
        key "schema": Any
        key "type": Union[str, ParameterType]
        allowedValues: list[Any]
        defaultValue: Any
        metadata: ParameterDefinitionsValueMetadata
        schema: Any
        type: Union[str, ParameterType]


    class azure.mgmt.resource.policy.types.ParameterDefinitionsValueMetadata(TypedDict, total=False):
        key "assignPermissions": bool
        key "description": str
        key "displayName": str
        key "strongType": str
        assignPermissions: bool
        description: str
        displayName: str
        strongType: str


    class azure.mgmt.resource.policy.types.ParameterValuesValue(TypedDict, total=False):
        key "value": Any
        value: Any


    class azure.mgmt.resource.policy.types.PolicyAssignment(ExtensionResource):
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('PolicyAssignmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: Identity
        location: str
        name: str
        properties: PolicyAssignmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.PolicyAssignmentProperties(TypedDict, total=False):
        key "assignmentType": Union[str, AssignmentType]
        key "definitionVersion": str
        key "description": str
        key "displayName": str
        key "effectiveDefinitionVersion": str
        key "enforcementMode": Union[str, EnforcementMode]
        key "instanceId": str
        key "latestDefinitionVersion": str
        key "metadata": Any
        key "policyDefinitionId": str
        key "scope": str
        key "selfServeExemptionSettings": ForwardRef('SelfServeExemptionSettings', module='types')
        assignmentType: Union[str, AssignmentType]
        definitionVersion: str
        description: str
        displayName: str
        effectiveDefinitionVersion: str
        enforcementMode: Union[str, EnforcementMode]
        instanceId: str
        latestDefinitionVersion: str
        metadata: Any
        nonComplianceMessages: list[NonComplianceMessage]
        notScopes: list[str]
        overrides: list[Override]
        parameters: dict[str, ParameterValuesValue]
        policyDefinitionId: str
        resourceSelectors: list[ResourceSelector]
        scope: str
        selfServeExemptionSettings: SelfServeExemptionSettings


    class azure.mgmt.resource.policy.types.PolicyAssignmentUpdate(TypedDict, total=False):
        key "identity": ForwardRef('Identity', module='types')
        key "location": str
        key "properties": ForwardRef('PolicyAssignmentUpdateProperties', module='types')
        identity: Identity
        location: str
        properties: PolicyAssignmentUpdateProperties


    class azure.mgmt.resource.policy.types.PolicyAssignmentUpdateProperties(TypedDict, total=False):
        key "selfServeExemptionSettings": ForwardRef('SelfServeExemptionSettings', module='types')
        overrides: list[Override]
        resourceSelectors: list[ResourceSelector]
        selfServeExemptionSettings: SelfServeExemptionSettings


    class azure.mgmt.resource.policy.types.PolicyDefinition(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PolicyDefinitionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PolicyDefinitionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.PolicyDefinitionGroup(TypedDict, total=False):
        key "additionalMetadataId": str
        key "category": str
        key "description": str
        key "displayName": str
        key "name": Required[str]
        additionalMetadataId: str
        category: str
        description: str
        displayName: str
        name: str


    class azure.mgmt.resource.policy.types.PolicyDefinitionProperties(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "externalEvaluationEnforcementSettings": ForwardRef('ExternalEvaluationEnforcementSettings', module='types')
        key "metadata": Any
        key "mode": str
        key "policyRule": Any
        key "policyType": Union[str, PolicyType]
        key "version": str
        description: str
        displayName: str
        externalEvaluationEnforcementSettings: ExternalEvaluationEnforcementSettings
        metadata: Any
        mode: str
        parameters: dict[str, ParameterDefinitionsValue]
        policyRule: Any
        policyType: Union[str, PolicyType]
        version: str
        versions: list[str]


    class azure.mgmt.resource.policy.types.PolicyDefinitionReference(TypedDict, total=False):
        key "definitionVersion": str
        key "effectiveDefinitionVersion": str
        key "latestDefinitionVersion": str
        key "policyDefinitionId": Required[str]
        key "policyDefinitionReferenceId": str
        definitionVersion: str
        effectiveDefinitionVersion: str
        groupNames: list[str]
        latestDefinitionVersion: str
        parameters: dict[str, ParameterValuesValue]
        policyDefinitionId: str
        policyDefinitionReferenceId: str


    class azure.mgmt.resource.policy.types.PolicyDefinitionVersion(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PolicyDefinitionVersionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PolicyDefinitionVersionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.PolicyDefinitionVersionProperties(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "externalEvaluationEnforcementSettings": ForwardRef('ExternalEvaluationEnforcementSettings', module='types')
        key "metadata": Any
        key "mode": str
        key "policyRule": Any
        key "policyType": Union[str, PolicyType]
        key "version": str
        description: str
        displayName: str
        externalEvaluationEnforcementSettings: ExternalEvaluationEnforcementSettings
        metadata: Any
        mode: str
        parameters: dict[str, ParameterDefinitionsValue]
        policyRule: Any
        policyType: Union[str, PolicyType]
        version: str


    class azure.mgmt.resource.policy.types.PolicyEnrollment(ExtensionResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('PolicyEnrollmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: PolicyEnrollmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.PolicyEnrollmentProperties(TypedDict, total=False):
        key "assignmentScopeValidation": Union[str, AssignmentScopeValidation]
        key "description": str
        key "displayName": str
        key "metadata": Any
        key "policyAssignmentId": Required[str]
        key "policyAssignmentInstanceId": str
        assignmentScopeValidation: Union[str, AssignmentScopeValidation]
        description: str
        displayName: str
        metadata: Any
        policyAssignmentId: str
        policyAssignmentInstanceId: str
        policyDefinitionReferenceIds: list[str]
        resourceSelectors: list[ResourceSelector]


    class azure.mgmt.resource.policy.types.PolicyEnrollmentUpdate(TypedDict, total=False):
        key "properties": ForwardRef('PolicyEnrollmentUpdateProperties', module='types')
        properties: PolicyEnrollmentUpdateProperties


    class azure.mgmt.resource.policy.types.PolicyEnrollmentUpdateProperties(TypedDict, total=False):
        key "assignmentScopeValidation": Union[str, AssignmentScopeValidation]
        assignmentScopeValidation: Union[str, AssignmentScopeValidation]
        resourceSelectors: list[ResourceSelector]


    class azure.mgmt.resource.policy.types.PolicyExemption(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PolicyExemptionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PolicyExemptionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.PolicyExemptionProperties(TypedDict, total=False):
        key "assignmentScopeValidation": Union[str, AssignmentScopeValidation]
        key "description": str
        key "displayName": str
        key "exemptionCategory": Required[Union[str, ExemptionCategory]]
        key "exemptionManagementMode": Union[str, ExemptionManagementMode]
        key "expiresOn": str
        key "metadata": Any
        key "policyAssignmentId": Required[str]
        assignmentScopeValidation: Union[str, AssignmentScopeValidation]
        description: str
        displayName: str
        exemptionCategory: Union[str, ExemptionCategory]
        exemptionManagementMode: Union[str, ExemptionManagementMode]
        expiresOn: str
        metadata: Any
        policyAssignmentId: str
        policyDefinitionReferenceIds: list[str]
        resourceSelectors: list[ResourceSelector]


    class azure.mgmt.resource.policy.types.PolicyExemptionUpdate(TypedDict, total=False):
        key "properties": ForwardRef('PolicyExemptionUpdateProperties', module='types')
        properties: PolicyExemptionUpdateProperties


    class azure.mgmt.resource.policy.types.PolicyExemptionUpdateProperties(TypedDict, total=False):
        key "assignmentScopeValidation": Union[str, AssignmentScopeValidation]
        key "exemptionManagementMode": Union[str, ExemptionManagementMode]
        assignmentScopeValidation: Union[str, AssignmentScopeValidation]
        exemptionManagementMode: Union[str, ExemptionManagementMode]
        resourceSelectors: list[ResourceSelector]


    class azure.mgmt.resource.policy.types.PolicySetDefinition(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PolicySetDefinitionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PolicySetDefinitionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.PolicySetDefinitionProperties(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "metadata": Any
        key "policyDefinitions": Required[list[PolicyDefinitionReference]]
        key "policyType": Union[str, PolicyType]
        key "version": str
        description: str
        displayName: str
        metadata: Any
        parameters: dict[str, ParameterDefinitionsValue]
        policyDefinitionGroups: list[PolicyDefinitionGroup]
        policyDefinitions: list[PolicyDefinitionReference]
        policyType: Union[str, PolicyType]
        version: str
        versions: list[str]


    class azure.mgmt.resource.policy.types.PolicySetDefinitionVersion(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PolicySetDefinitionVersionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PolicySetDefinitionVersionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.PolicySetDefinitionVersionProperties(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "metadata": Any
        key "policyDefinitions": Required[list[PolicyDefinitionReference]]
        key "policyType": Union[str, PolicyType]
        key "version": str
        description: str
        displayName: str
        metadata: Any
        parameters: dict[str, ParameterDefinitionsValue]
        policyDefinitionGroups: list[PolicyDefinitionGroup]
        policyDefinitions: list[PolicyDefinitionReference]
        policyType: Union[str, PolicyType]
        version: str


    class azure.mgmt.resource.policy.types.PolicyTokenOperation(TypedDict, total=False):
        key "content": Any
        key "httpMethod": Required[str]
        key "uri": Required[str]
        content: Any
        httpMethod: str
        uri: str


    class azure.mgmt.resource.policy.types.PolicyTokenRequest(TypedDict, total=False):
        key "changeReference": str
        key "operation": Required[PolicyTokenOperation]
        changeReference: str
        operation: PolicyTokenOperation


    class azure.mgmt.resource.policy.types.PolicyVariableColumn(TypedDict, total=False):
        key "columnName": Required[str]
        columnName: str


    class azure.mgmt.resource.policy.types.PolicyVariableProperties(TypedDict, total=False):
        key "columns": Required[list[PolicyVariableColumn]]
        columns: list[PolicyVariableColumn]


    class azure.mgmt.resource.policy.types.PolicyVariableValueColumnValue(TypedDict, total=False):
        key "columnName": Required[str]
        key "columnValue": Required[Any]
        columnName: str
        columnValue: Any


    class azure.mgmt.resource.policy.types.PolicyVariableValueProperties(TypedDict, total=False):
        key "values": Required[list[PolicyVariableValueColumnValue]]
        values: list[PolicyVariableValueColumnValue]


    class azure.mgmt.resource.policy.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.ResourceSelector(TypedDict, total=False):
        key "name": str
        name: str
        selectors: list[Selector]


    class azure.mgmt.resource.policy.types.Selector(TypedDict):
        key "kind": Union[str, SelectorKind]
        in: list[str]
        kind: Union[str, SelectorKind]
        notIn: list[str]


    class azure.mgmt.resource.policy.types.SelfServeExemptionSettings(TypedDict, total=False):
        key "enabled": bool
        enabled: bool
        policyDefinitionReferenceIds: list[str]


    class azure.mgmt.resource.policy.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.resource.policy.types.UserAssignedIdentitiesValue(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.resource.policy.types.Variable(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PolicyVariableProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PolicyVariableProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resource.policy.types.VariableValue(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PolicyVariableValueProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PolicyVariableValueProperties
        systemData: SystemData
        type: str


```