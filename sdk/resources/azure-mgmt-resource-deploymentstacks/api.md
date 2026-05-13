```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.resource.deploymentstacks

    class azure.mgmt.resource.deploymentstacks.DeploymentStacksClient: implements ContextManager 
        deployment_stacks: DeploymentStacksOperations
        deployment_stacks_what_if_results_at_management_group: DeploymentStacksWhatIfResultsAtManagementGroupOperations
        deployment_stacks_what_if_results_at_resource_group: DeploymentStacksWhatIfResultsAtResourceGroupOperations
        deployment_stacks_what_if_results_at_subscription: DeploymentStacksWhatIfResultsAtSubscriptionOperations

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


namespace azure.mgmt.resource.deploymentstacks.aio

    class azure.mgmt.resource.deploymentstacks.aio.DeploymentStacksClient: implements AsyncContextManager 
        deployment_stacks: DeploymentStacksOperations
        deployment_stacks_what_if_results_at_management_group: DeploymentStacksWhatIfResultsAtManagementGroupOperations
        deployment_stacks_what_if_results_at_resource_group: DeploymentStacksWhatIfResultsAtResourceGroupOperations
        deployment_stacks_what_if_results_at_subscription: DeploymentStacksWhatIfResultsAtSubscriptionOperations

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


namespace azure.mgmt.resource.deploymentstacks.aio.operations

    class azure.mgmt.resource.deploymentstacks.aio.operations.DeploymentStacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStack]: ...

        @overload
        async def begin_create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStack]: ...

        @overload
        async def begin_create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStack]: ...

        @overload
        async def begin_create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStack]: ...

        @overload
        async def begin_create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStack]: ...

        @overload
        async def begin_create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStack]: ...

        @overload
        async def begin_create_or_update_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStack]: ...

        @overload
        async def begin_create_or_update_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStack]: ...

        @overload
        async def begin_create_or_update_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStack]: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'2025-07-01': ['unmanage_action_resources_without_delete_support'], '2024-03-01': ['bypass_stack_out_of_sync_error']}, api_versions_list=['2022-08-01-preview', '2024-03-01', '2025-07-01'])
        async def begin_delete_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'2025-07-01': ['unmanage_action_resources_without_delete_support'], '2024-03-01': ['bypass_stack_out_of_sync_error']}, api_versions_list=['2022-08-01-preview', '2024-03-01', '2025-07-01'])
        async def begin_delete_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'2025-07-01': ['unmanage_action_resources_without_delete_support'], '2024-03-01': ['bypass_stack_out_of_sync_error']}, api_versions_list=['2022-08-01-preview', '2024-03-01', '2025-07-01'])
        async def begin_delete_at_subscription(
                self, 
                deployment_stack_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate_stack_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStackValidateResult]: ...

        @overload
        async def begin_validate_stack_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStackValidateResult]: ...

        @overload
        async def begin_validate_stack_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStackValidateResult]: ...

        @overload
        async def begin_validate_stack_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStackValidateResult]: ...

        @overload
        async def begin_validate_stack_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStackValidateResult]: ...

        @overload
        async def begin_validate_stack_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStackValidateResult]: ...

        @overload
        async def begin_validate_stack_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStackValidateResult]: ...

        @overload
        async def begin_validate_stack_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStackValidateResult]: ...

        @overload
        async def begin_validate_stack_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStackValidateResult]: ...

        @distributed_trace_async
        async def export_template_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStackTemplateDefinition: ...

        @distributed_trace_async
        async def export_template_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStackTemplateDefinition: ...

        @distributed_trace_async
        async def export_template_at_subscription(
                self, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStackTemplateDefinition: ...

        @distributed_trace_async
        async def get_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStack: ...

        @distributed_trace_async
        async def get_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStack: ...

        @distributed_trace_async
        async def get_at_subscription(
                self, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStack: ...

        @distributed_trace
        def list_at_management_group(
                self, 
                management_group_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentStack]: ...

        @distributed_trace
        def list_at_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentStack]: ...

        @distributed_trace
        def list_at_subscription(self, **kwargs: Any) -> AsyncItemPaged[DeploymentStack]: ...


    class azure.mgmt.resource.deploymentstacks.aio.operations.DeploymentStacksWhatIfResultsAtManagementGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: DeploymentStacksWhatIfResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'management_group_id', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        async def begin_what_if(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'management_group_id', 'deployment_stacks_what_if_result_name', 'unmanage_action_resources', 'unmanage_action_resource_groups', 'unmanage_action_management_groups', 'unmanage_action_resources_without_delete_support', 'bypass_stack_out_of_sync_error']}, api_versions_list=['2025-07-01'])
        async def delete(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'management_group_id', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        async def get(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> DeploymentStacksWhatIfResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'management_group_id', 'accept']}, api_versions_list=['2025-07-01'])
        def list(
                self, 
                management_group_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentStacksWhatIfResult]: ...


    class azure.mgmt.resource.deploymentstacks.aio.operations.DeploymentStacksWhatIfResultsAtResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: DeploymentStacksWhatIfResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        async def begin_what_if(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'deployment_stacks_what_if_result_name', 'unmanage_action_resources', 'unmanage_action_resource_groups', 'unmanage_action_management_groups', 'unmanage_action_resources_without_delete_support', 'bypass_stack_out_of_sync_error']}, api_versions_list=['2025-07-01'])
        async def delete(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> DeploymentStacksWhatIfResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentStacksWhatIfResult]: ...


    class azure.mgmt.resource.deploymentstacks.aio.operations.DeploymentStacksWhatIfResultsAtSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                deployment_stacks_what_if_result_name: str, 
                resource: DeploymentStacksWhatIfResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                deployment_stacks_what_if_result_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                deployment_stacks_what_if_result_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        async def begin_what_if(
                self, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'deployment_stacks_what_if_result_name', 'unmanage_action_resources', 'unmanage_action_resource_groups', 'unmanage_action_management_groups', 'unmanage_action_resources_without_delete_support', 'bypass_stack_out_of_sync_error']}, api_versions_list=['2025-07-01'])
        async def delete(
                self, 
                deployment_stacks_what_if_result_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        async def get(
                self, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> DeploymentStacksWhatIfResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-01'])
        def list(self, **kwargs: Any) -> AsyncItemPaged[DeploymentStacksWhatIfResult]: ...


namespace azure.mgmt.resource.deploymentstacks.models

    class azure.mgmt.resource.deploymentstacks.models.ActionOnUnmanage(_Model):
        management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]]
        resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]]
        resources: Union[str, UnmanageActionResourceMode]
        resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]]

        @overload
        def __init__(
                self, 
                *, 
                management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                resources: Union[str, UnmanageActionResourceMode], 
                resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resource.deploymentstacks.models.DenySettings(_Model):
        apply_to_child_scopes: Optional[bool]
        excluded_actions: Optional[list[str]]
        excluded_principals: Optional[list[str]]
        mode: Union[str, DenySettingsMode]

        @overload
        def __init__(
                self, 
                *, 
                apply_to_child_scopes: Optional[bool] = ..., 
                excluded_actions: Optional[list[str]] = ..., 
                excluded_principals: Optional[list[str]] = ..., 
                mode: Union[str, DenySettingsMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DenySettingsMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DENY_DELETE = "denyDelete"
        DENY_WRITE_AND_DELETE = "denyWriteAndDelete"
        NONE = "none"


    class azure.mgmt.resource.deploymentstacks.models.DenyStatusMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DENY_DELETE = "denyDelete"
        DENY_WRITE_AND_DELETE = "denyWriteAndDelete"
        INAPPLICABLE = "inapplicable"
        NONE = "none"
        NOT_SUPPORTED = "notSupported"
        REMOVED_BY_SYSTEM = "removedBySystem"
        UNKNOWN = "unknown"


    class azure.mgmt.resource.deploymentstacks.models.DeploymentExtension(_Model):
        config: Optional[DeploymentExtensionConfig]
        config_id: Optional[str]
        name: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                config: Optional[DeploymentExtensionConfig] = ..., 
                config_id: Optional[str] = ..., 
                name: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentExtensionConfig(_Model):


    class azure.mgmt.resource.deploymentstacks.models.DeploymentExtensionConfigItem(_Model):
        key_vault_reference: Optional[KeyVaultParameterReference]
        type: Optional[str]
        value: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_reference: Optional[KeyVaultParameterReference] = ..., 
                value: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentExternalInput(_Model):
        value: Any

        @overload
        def __init__(
                self, 
                *, 
                value: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentExternalInputDefinition(_Model):
        config: Optional[Any]
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                config: Optional[Any] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentParameter(_Model):
        expression: Optional[str]
        reference: Optional[KeyVaultParameterReference]
        type: Optional[str]
        value: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                expression: Optional[str] = ..., 
                reference: Optional[KeyVaultParameterReference] = ..., 
                type: Optional[str] = ..., 
                value: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStack(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[DeploymentStackProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[DeploymentStackProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStackProperties(_Model):
        action_on_unmanage: ActionOnUnmanage
        bypass_stack_out_of_sync_error: Optional[bool]
        correlation_id: Optional[str]
        debug_setting: Optional[DeploymentStacksDebugSetting]
        deleted_resources: Optional[list[ResourceReference]]
        deny_settings: DenySettings
        deployment_extensions: Optional[list[DeploymentExtension]]
        deployment_id: Optional[str]
        deployment_scope: Optional[str]
        description: Optional[str]
        detached_resources: Optional[list[ResourceReference]]
        duration: Optional[str]
        error: Optional[ErrorDetail]
        extension_configs: Optional[dict[str, DeploymentExtensionConfig]]
        external_input_definitions: Optional[dict[str, DeploymentExternalInputDefinition]]
        external_inputs: Optional[dict[str, DeploymentExternalInput]]
        failed_resources: Optional[list[ResourceReferenceExtended]]
        outputs: Optional[dict[str, Any]]
        parameters: Optional[dict[str, DeploymentParameter]]
        parameters_link: Optional[DeploymentStacksParametersLink]
        provisioning_state: Optional[Union[str, DeploymentStackProvisioningState]]
        resources: Optional[list[ManagedResourceReference]]
        template: Optional[dict[str, Any]]
        template_link: Optional[DeploymentStacksTemplateLink]
        validation_level: Optional[Union[str, ValidationLevel]]

        @overload
        def __init__(
                self, 
                *, 
                action_on_unmanage: ActionOnUnmanage, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                debug_setting: Optional[DeploymentStacksDebugSetting] = ..., 
                deny_settings: DenySettings, 
                deployment_scope: Optional[str] = ..., 
                description: Optional[str] = ..., 
                extension_configs: Optional[dict[str, DeploymentExtensionConfig]] = ..., 
                external_input_definitions: Optional[dict[str, DeploymentExternalInputDefinition]] = ..., 
                external_inputs: Optional[dict[str, DeploymentExternalInput]] = ..., 
                parameters: Optional[dict[str, DeploymentParameter]] = ..., 
                parameters_link: Optional[DeploymentStacksParametersLink] = ..., 
                template: Optional[dict[str, Any]] = ..., 
                template_link: Optional[DeploymentStacksTemplateLink] = ..., 
                validation_level: Optional[Union[str, ValidationLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStackProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "canceled"
        CANCELING = "canceling"
        CREATING = "creating"
        DELETING = "deleting"
        DELETING_RESOURCES = "deletingResources"
        DEPLOYING = "deploying"
        FAILED = "failed"
        INITIALIZING = "initializing"
        RUNNING = "running"
        SUCCEEDED = "succeeded"
        UPDATING_DENY_ASSIGNMENTS = "updatingDenyAssignments"
        VALIDATING = "validating"
        WAITING = "waiting"


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStackTemplateDefinition(_Model):
        template: Optional[dict[str, Any]]
        template_link: Optional[DeploymentStacksTemplateLink]

        @overload
        def __init__(
                self, 
                *, 
                template: Optional[dict[str, Any]] = ..., 
                template_link: Optional[DeploymentStacksTemplateLink] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStackValidateProperties(_Model):
        action_on_unmanage: Optional[ActionOnUnmanage]
        correlation_id: Optional[str]
        deny_settings: Optional[DenySettings]
        deployment_extensions: Optional[list[DeploymentExtension]]
        deployment_scope: Optional[str]
        description: Optional[str]
        parameters: Optional[dict[str, DeploymentParameter]]
        template_link: Optional[DeploymentStacksTemplateLink]
        validated_resources: Optional[list[ResourceReference]]
        validation_level: Optional[Union[str, ValidationLevel]]

        @overload
        def __init__(
                self, 
                *, 
                action_on_unmanage: Optional[ActionOnUnmanage] = ..., 
                correlation_id: Optional[str] = ..., 
                deny_settings: Optional[DenySettings] = ..., 
                deployment_extensions: Optional[list[DeploymentExtension]] = ..., 
                deployment_scope: Optional[str] = ..., 
                description: Optional[str] = ..., 
                parameters: Optional[dict[str, DeploymentParameter]] = ..., 
                template_link: Optional[DeploymentStacksTemplateLink] = ..., 
                validated_resources: Optional[list[ResourceReference]] = ..., 
                validation_level: Optional[Union[str, ValidationLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStackValidateResult(_Model):
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[DeploymentStackValidateProperties]
        system_data: Optional[SystemData]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeploymentStackValidateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksChangeBase(_Model):
        after: Optional[str]
        before: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                after: Optional[str] = ..., 
                before: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksChangeBaseDenyStatusMode(_Model):
        after: Optional[Union[str, DenyStatusMode]]
        before: Optional[Union[str, DenyStatusMode]]

        @overload
        def __init__(
                self, 
                *, 
                after: Optional[Union[str, DenyStatusMode]] = ..., 
                before: Optional[Union[str, DenyStatusMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksChangeBaseDeploymentStacksManagementStatus(_Model):
        after: Optional[Union[str, DeploymentStacksManagementStatus]]
        before: Optional[Union[str, DeploymentStacksManagementStatus]]

        @overload
        def __init__(
                self, 
                *, 
                after: Optional[Union[str, DeploymentStacksManagementStatus]] = ..., 
                before: Optional[Union[str, DeploymentStacksManagementStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksChangeDeltaDenySettings(_Model):
        after: Optional[DenySettings]
        before: Optional[DenySettings]
        delta: Optional[list[DeploymentStacksWhatIfPropertyChange]]

        @overload
        def __init__(
                self, 
                *, 
                after: Optional[DenySettings] = ..., 
                before: Optional[DenySettings] = ..., 
                delta: Optional[list[DeploymentStacksWhatIfPropertyChange]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksChangeDeltaRecord(_Model):
        after: Optional[dict[str, Any]]
        before: Optional[dict[str, Any]]
        delta: Optional[list[DeploymentStacksWhatIfPropertyChange]]

        @overload
        def __init__(
                self, 
                *, 
                after: Optional[dict[str, Any]] = ..., 
                before: Optional[dict[str, Any]] = ..., 
                delta: Optional[list[DeploymentStacksWhatIfPropertyChange]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksDebugSetting(_Model):
        detail_level: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                detail_level: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksDiagnostic(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: str
        level: Union[str, DeploymentStacksDiagnosticLevel]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[list[ErrorAdditionalInfo]] = ..., 
                code: str, 
                level: Union[str, DeploymentStacksDiagnosticLevel], 
                message: str, 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksDiagnosticLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "error"
        INFO = "info"
        WARNING = "warning"


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksManagementStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "managed"
        UNKNOWN = "unknown"
        UNMANAGED = "unmanaged"


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksParametersLink(_Model):
        content_version: Optional[str]
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                content_version: Optional[str] = ..., 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksTemplateLink(_Model):
        content_version: Optional[str]
        id: Optional[str]
        query_string: Optional[str]
        relative_path: Optional[str]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_version: Optional[str] = ..., 
                id: Optional[str] = ..., 
                query_string: Optional[str] = ..., 
                relative_path: Optional[str] = ..., 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksWhatIfChange(_Model):
        deny_settings_change: DeploymentStacksChangeDeltaDenySettings
        deployment_scope_change: Optional[DeploymentStacksChangeBase]
        resource_changes: list[DeploymentStacksWhatIfResourceChange]

        @overload
        def __init__(
                self, 
                *, 
                deny_settings_change: DeploymentStacksChangeDeltaDenySettings, 
                deployment_scope_change: Optional[DeploymentStacksChangeBase] = ..., 
                resource_changes: list[DeploymentStacksWhatIfResourceChange]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksWhatIfChangeCertainty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFINITE = "definite"
        POTENTIAL = "potential"


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksWhatIfChangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "create"
        DELETE = "delete"
        DETACH = "detach"
        MODIFY = "modify"
        NO_CHANGE = "noChange"
        UNSUPPORTED = "unsupported"


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksWhatIfPropertyChange(_Model):
        after: Optional[Any]
        before: Optional[Any]
        change_type: Union[str, DeploymentStacksWhatIfPropertyChangeType]
        children: Optional[list[DeploymentStacksWhatIfPropertyChange]]
        path: str

        @overload
        def __init__(
                self, 
                *, 
                after: Optional[Any] = ..., 
                before: Optional[Any] = ..., 
                change_type: Union[str, DeploymentStacksWhatIfPropertyChangeType], 
                children: Optional[list[DeploymentStacksWhatIfPropertyChange]] = ..., 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksWhatIfPropertyChangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "array"
        CREATE = "create"
        DELETE = "delete"
        MODIFY = "modify"
        NO_EFFECT = "noEffect"


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksWhatIfResourceChange(_Model):
        api_version: Optional[str]
        change_certainty: Union[str, DeploymentStacksWhatIfChangeCertainty]
        change_type: Union[str, DeploymentStacksWhatIfChangeType]
        deny_status_change: Optional[DeploymentStacksChangeBaseDenyStatusMode]
        deployment_id: Optional[str]
        extension: Optional[DeploymentExtension]
        id: Optional[str]
        identifiers: Optional[dict[str, Any]]
        management_status_change: Optional[DeploymentStacksChangeBaseDeploymentStacksManagementStatus]
        resource_configuration_changes: Optional[DeploymentStacksChangeDeltaRecord]
        symbolic_name: Optional[str]
        type: Optional[str]
        unsupported_reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                change_certainty: Union[str, DeploymentStacksWhatIfChangeCertainty], 
                change_type: Union[str, DeploymentStacksWhatIfChangeType], 
                deny_status_change: Optional[DeploymentStacksChangeBaseDenyStatusMode] = ..., 
                deployment_id: Optional[str] = ..., 
                management_status_change: Optional[DeploymentStacksChangeBaseDeploymentStacksManagementStatus] = ..., 
                resource_configuration_changes: Optional[DeploymentStacksChangeDeltaRecord] = ..., 
                symbolic_name: Optional[str] = ..., 
                unsupported_reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksWhatIfResult(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[DeploymentStacksWhatIfResultProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[DeploymentStacksWhatIfResultProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.DeploymentStacksWhatIfResultProperties(_Model):
        action_on_unmanage: ActionOnUnmanage
        changes: Optional[DeploymentStacksWhatIfChange]
        correlation_id: Optional[str]
        debug_setting: Optional[DeploymentStacksDebugSetting]
        deny_settings: DenySettings
        deployment_scope: Optional[str]
        deployment_stack_last_modified: Optional[datetime]
        deployment_stack_resource_id: str
        description: Optional[str]
        diagnostics: Optional[list[DeploymentStacksDiagnostic]]
        error: Optional[ErrorDetail]
        extension_configs: Optional[dict[str, DeploymentExtensionConfig]]
        external_input_definitions: Optional[dict[str, DeploymentExternalInputDefinition]]
        external_inputs: Optional[dict[str, DeploymentExternalInput]]
        parameters: Optional[dict[str, DeploymentParameter]]
        parameters_link: Optional[DeploymentStacksParametersLink]
        provisioning_state: Optional[Union[str, DeploymentStackProvisioningState]]
        retention_interval: timedelta
        template: Optional[dict[str, Any]]
        template_link: Optional[DeploymentStacksTemplateLink]
        validation_level: Optional[Union[str, ValidationLevel]]

        @overload
        def __init__(
                self, 
                *, 
                action_on_unmanage: ActionOnUnmanage, 
                debug_setting: Optional[DeploymentStacksDebugSetting] = ..., 
                deny_settings: DenySettings, 
                deployment_scope: Optional[str] = ..., 
                deployment_stack_resource_id: str, 
                description: Optional[str] = ..., 
                extension_configs: Optional[dict[str, DeploymentExtensionConfig]] = ..., 
                external_input_definitions: Optional[dict[str, DeploymentExternalInputDefinition]] = ..., 
                external_inputs: Optional[dict[str, DeploymentExternalInput]] = ..., 
                parameters: Optional[dict[str, DeploymentParameter]] = ..., 
                parameters_link: Optional[DeploymentStacksParametersLink] = ..., 
                retention_interval: timedelta, 
                template: Optional[dict[str, Any]] = ..., 
                template_link: Optional[DeploymentStacksTemplateLink] = ..., 
                validation_level: Optional[Union[str, ValidationLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.resource.deploymentstacks.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.resource.deploymentstacks.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.KeyVaultParameterReference(_Model):
        key_vault: KeyVaultReference
        secret_name: str
        secret_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_vault: KeyVaultReference, 
                secret_name: str, 
                secret_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.KeyVaultReference(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.ManagedResourceReference(ResourceReference):
        api_version: str
        deny_status: Optional[Union[str, DenyStatusMode]]
        extension: DeploymentExtension
        id: str
        identifiers: dict[str, any]
        status: Optional[Union[str, ResourceStatusMode]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                deny_status: Optional[Union[str, DenyStatusMode]] = ..., 
                status: Optional[Union[str, ResourceStatusMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.deploymentstacks.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resource.deploymentstacks.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.resource.deploymentstacks.models.ResourceReference(_Model):
        api_version: Optional[str]
        extension: Optional[DeploymentExtension]
        id: Optional[str]
        identifiers: Optional[dict[str, Any]]
        type: Optional[str]


    class azure.mgmt.resource.deploymentstacks.models.ResourceReferenceExtended(_Model):
        api_version: Optional[str]
        error: Optional[ErrorDetail]
        extension: Optional[DeploymentExtension]
        id: Optional[str]
        identifiers: Optional[dict[str, Any]]
        type: Optional[str]


    class azure.mgmt.resource.deploymentstacks.models.ResourceStatusMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE_FAILED = "deleteFailed"
        MANAGED = "managed"
        REMOVE_DENY_FAILED = "removeDenyFailed"


    class azure.mgmt.resource.deploymentstacks.models.ResourcesWithoutDeleteSupportAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DETACH = "detach"
        FAIL = "fail"


    class azure.mgmt.resource.deploymentstacks.models.SystemData(_Model):
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


    class azure.mgmt.resource.deploymentstacks.models.UnmanageActionManagementGroupMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "delete"
        DETACH = "detach"


    class azure.mgmt.resource.deploymentstacks.models.UnmanageActionResourceGroupMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "delete"
        DETACH = "detach"


    class azure.mgmt.resource.deploymentstacks.models.UnmanageActionResourceMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "delete"
        DETACH = "detach"


    class azure.mgmt.resource.deploymentstacks.models.ValidationLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROVIDER = "Provider"
        PROVIDER_NO_RBAC = "ProviderNoRbac"
        TEMPLATE = "Template"


namespace azure.mgmt.resource.deploymentstacks.operations

    class azure.mgmt.resource.deploymentstacks.operations.DeploymentStacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStack]: ...

        @overload
        def begin_create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStack]: ...

        @overload
        def begin_create_or_update_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStack]: ...

        @overload
        def begin_create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStack]: ...

        @overload
        def begin_create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStack]: ...

        @overload
        def begin_create_or_update_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStack]: ...

        @overload
        def begin_create_or_update_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStack]: ...

        @overload
        def begin_create_or_update_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStack]: ...

        @overload
        def begin_create_or_update_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStack]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2025-07-01': ['unmanage_action_resources_without_delete_support'], '2024-03-01': ['bypass_stack_out_of_sync_error']}, api_versions_list=['2022-08-01-preview', '2024-03-01', '2025-07-01'])
        def begin_delete_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2025-07-01': ['unmanage_action_resources_without_delete_support'], '2024-03-01': ['bypass_stack_out_of_sync_error']}, api_versions_list=['2022-08-01-preview', '2024-03-01', '2025-07-01'])
        def begin_delete_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2025-07-01': ['unmanage_action_resources_without_delete_support'], '2024-03-01': ['bypass_stack_out_of_sync_error']}, api_versions_list=['2022-08-01-preview', '2024-03-01', '2025-07-01'])
        def begin_delete_at_subscription(
                self, 
                deployment_stack_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate_stack_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStackValidateResult]: ...

        @overload
        def begin_validate_stack_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStackValidateResult]: ...

        @overload
        def begin_validate_stack_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStackValidateResult]: ...

        @overload
        def begin_validate_stack_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStackValidateResult]: ...

        @overload
        def begin_validate_stack_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStackValidateResult]: ...

        @overload
        def begin_validate_stack_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStackValidateResult]: ...

        @overload
        def begin_validate_stack_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: DeploymentStack, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStackValidateResult]: ...

        @overload
        def begin_validate_stack_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStackValidateResult]: ...

        @overload
        def begin_validate_stack_at_subscription(
                self, 
                deployment_stack_name: str, 
                deployment_stack: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStackValidateResult]: ...

        @distributed_trace
        def export_template_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStackTemplateDefinition: ...

        @distributed_trace
        def export_template_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStackTemplateDefinition: ...

        @distributed_trace
        def export_template_at_subscription(
                self, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStackTemplateDefinition: ...

        @distributed_trace
        def get_at_management_group(
                self, 
                management_group_id: str, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStack: ...

        @distributed_trace
        def get_at_resource_group(
                self, 
                resource_group_name: str, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStack: ...

        @distributed_trace
        def get_at_subscription(
                self, 
                deployment_stack_name: str, 
                **kwargs: Any
            ) -> DeploymentStack: ...

        @distributed_trace
        def list_at_management_group(
                self, 
                management_group_id: str, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentStack]: ...

        @distributed_trace
        def list_at_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentStack]: ...

        @distributed_trace
        def list_at_subscription(self, **kwargs: Any) -> ItemPaged[DeploymentStack]: ...


    class azure.mgmt.resource.deploymentstacks.operations.DeploymentStacksWhatIfResultsAtManagementGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: DeploymentStacksWhatIfResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'management_group_id', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        def begin_what_if(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'management_group_id', 'deployment_stacks_what_if_result_name', 'unmanage_action_resources', 'unmanage_action_resource_groups', 'unmanage_action_management_groups', 'unmanage_action_resources_without_delete_support', 'bypass_stack_out_of_sync_error']}, api_versions_list=['2025-07-01'])
        def delete(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'management_group_id', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        def get(
                self, 
                management_group_id: str, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> DeploymentStacksWhatIfResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'management_group_id', 'accept']}, api_versions_list=['2025-07-01'])
        def list(
                self, 
                management_group_id: str, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentStacksWhatIfResult]: ...


    class azure.mgmt.resource.deploymentstacks.operations.DeploymentStacksWhatIfResultsAtResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: DeploymentStacksWhatIfResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        def begin_what_if(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'deployment_stacks_what_if_result_name', 'unmanage_action_resources', 'unmanage_action_resource_groups', 'unmanage_action_management_groups', 'unmanage_action_resources_without_delete_support', 'bypass_stack_out_of_sync_error']}, api_versions_list=['2025-07-01'])
        def delete(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> DeploymentStacksWhatIfResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-01'])
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentStacksWhatIfResult]: ...


    class azure.mgmt.resource.deploymentstacks.operations.DeploymentStacksWhatIfResultsAtSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                deployment_stacks_what_if_result_name: str, 
                resource: DeploymentStacksWhatIfResult, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                deployment_stacks_what_if_result_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                deployment_stacks_what_if_result_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        def begin_what_if(
                self, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> LROPoller[DeploymentStacksWhatIfResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'deployment_stacks_what_if_result_name', 'unmanage_action_resources', 'unmanage_action_resource_groups', 'unmanage_action_management_groups', 'unmanage_action_resources_without_delete_support', 'bypass_stack_out_of_sync_error']}, api_versions_list=['2025-07-01'])
        def delete(
                self, 
                deployment_stacks_what_if_result_name: str, 
                *, 
                bypass_stack_out_of_sync_error: Optional[bool] = ..., 
                unmanage_action_management_groups: Optional[Union[str, UnmanageActionManagementGroupMode]] = ..., 
                unmanage_action_resource_groups: Optional[Union[str, UnmanageActionResourceGroupMode]] = ..., 
                unmanage_action_resources: Optional[Union[str, UnmanageActionResourceMode]] = ..., 
                unmanage_action_resources_without_delete_support: Optional[Union[str, ResourcesWithoutDeleteSupportAction]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'deployment_stacks_what_if_result_name', 'accept']}, api_versions_list=['2025-07-01'])
        def get(
                self, 
                deployment_stacks_what_if_result_name: str, 
                **kwargs: Any
            ) -> DeploymentStacksWhatIfResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01', params_added_on={'2025-07-01': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-01'])
        def list(self, **kwargs: Any) -> ItemPaged[DeploymentStacksWhatIfResult]: ...


```