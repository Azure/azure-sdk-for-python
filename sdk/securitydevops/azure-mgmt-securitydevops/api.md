```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.securitydevops

    class azure.mgmt.securitydevops.MicrosoftSecurityDevOps: implements ContextManager 
        azure_dev_ops_connector: AzureDevOpsConnectorOperations
        azure_dev_ops_connector_stats: AzureDevOpsConnectorStatsOperations
        azure_dev_ops_org: AzureDevOpsOrgOperations
        azure_dev_ops_project: AzureDevOpsProjectOperations
        azure_dev_ops_repo: AzureDevOpsRepoOperations
        git_hub_connector: GitHubConnectorOperations
        git_hub_connector_stats: GitHubConnectorStatsOperations
        git_hub_owner: GitHubOwnerOperations
        git_hub_repo: GitHubRepoOperations
        operations: Operations

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


namespace azure.mgmt.securitydevops.aio

    class azure.mgmt.securitydevops.aio.MicrosoftSecurityDevOps: implements AsyncContextManager 
        azure_dev_ops_connector: AzureDevOpsConnectorOperations
        azure_dev_ops_connector_stats: AzureDevOpsConnectorStatsOperations
        azure_dev_ops_org: AzureDevOpsOrgOperations
        azure_dev_ops_project: AzureDevOpsProjectOperations
        azure_dev_ops_repo: AzureDevOpsRepoOperations
        git_hub_connector: GitHubConnectorOperations
        git_hub_connector_stats: GitHubConnectorStatsOperations
        git_hub_owner: GitHubOwnerOperations
        git_hub_repo: GitHubRepoOperations
        operations: Operations

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


namespace azure.mgmt.securitydevops.aio.operations

    class azure.mgmt.securitydevops.aio.operations.AzureDevOpsConnectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_connector: AzureDevOpsConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsConnector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_connector: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsConnector]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_connector: Optional[AzureDevOpsConnector] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsConnector]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_connector: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsConnector]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureDevOpsConnector: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureDevOpsConnector]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureDevOpsConnector]: ...


    class azure.mgmt.securitydevops.aio.operations.AzureDevOpsConnectorStatsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureDevOpsConnectorStatsListResponse: ...


    class azure.mgmt.securitydevops.aio.operations.AzureDevOpsOrgOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_org: AzureDevOpsOrg, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsOrg]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_org: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsOrg]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_org: Optional[AzureDevOpsOrg] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsOrg]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_org: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsOrg]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureDevOpsOrg: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureDevOpsOrg]: ...


    class azure.mgmt.securitydevops.aio.operations.AzureDevOpsProjectOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_project: AzureDevOpsProject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsProject]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_project: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsProject]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_project: Optional[AzureDevOpsProject] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsProject]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_project: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsProject]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureDevOpsProject: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureDevOpsProject]: ...


    class azure.mgmt.securitydevops.aio.operations.AzureDevOpsRepoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_repo_name: str, 
                azure_dev_ops_repo: AzureDevOpsRepo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsRepo]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_repo_name: str, 
                azure_dev_ops_repo: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsRepo]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_repo_name: str, 
                azure_dev_ops_repo: Optional[AzureDevOpsRepo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsRepo]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_repo_name: str, 
                azure_dev_ops_repo: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureDevOpsRepo]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_repo_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureDevOpsRepo: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureDevOpsRepo]: ...

        @distributed_trace
        def list_by_connector(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureDevOpsRepo]: ...


    class azure.mgmt.securitydevops.aio.operations.GitHubConnectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_connector: GitHubConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubConnector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_connector: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubConnector]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_connector: Optional[GitHubConnector] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubConnector]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_connector: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubConnector]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubConnector: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GitHubConnector]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GitHubConnector]: ...


    class azure.mgmt.securitydevops.aio.operations.GitHubConnectorStatsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubConnectorStatsListResponse: ...


    class azure.mgmt.securitydevops.aio.operations.GitHubOwnerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_owner: GitHubOwner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubOwner]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_owner: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubOwner]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_owner: Optional[GitHubOwner] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubOwner]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_owner: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubOwner]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubOwner: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GitHubOwner]: ...


    class azure.mgmt.securitydevops.aio.operations.GitHubRepoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_repo_name: str, 
                git_hub_repo: GitHubRepo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubRepo]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_repo_name: str, 
                git_hub_repo: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubRepo]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_repo_name: str, 
                git_hub_repo: Optional[GitHubRepo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubRepo]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_repo_name: str, 
                git_hub_repo: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GitHubRepo]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_repo_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubRepo: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GitHubRepo]: ...

        @distributed_trace
        def list_by_connector(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GitHubRepo]: ...


    class azure.mgmt.securitydevops.aio.operations.Operations:

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


namespace azure.mgmt.securitydevops.models

    class azure.mgmt.securitydevops.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.securitydevops.models.ActionableRemediation(Model):
        branch_configuration: TargetBranchConfiguration
        categories: Union[list[str, RuleCategory]]
        severity_levels: list[str]
        state: Union[str, ActionableRemediationState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                branch_configuration: Optional[TargetBranchConfiguration] = ..., 
                categories: Optional[List[Union[str, RuleCategory]]] = ..., 
                severity_levels: Optional[List[str]] = ..., 
                state: Optional[Union[str, ActionableRemediationState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.ActionableRemediationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NONE = "None"


    class azure.mgmt.securitydevops.models.AuthorizationInfo(Model):
        code: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AutoDiscovery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.securitydevops.models.AzureDevOpsConnector(TrackedResource):
        id: str
        location: str
        name: str
        properties: AzureDevOpsConnectorProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AzureDevOpsConnectorProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsConnectorListResponse(Model):
        next_link: str
        value: list[AzureDevOpsConnector]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AzureDevOpsConnector]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsConnectorProperties(Model):
        authorization: AuthorizationInfo
        orgs: list[AzureDevOpsOrgMetadata]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                authorization: Optional[AuthorizationInfo] = ..., 
                orgs: Optional[List[AzureDevOpsOrgMetadata]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsConnectorStats(ProxyResource):
        id: str
        name: str
        properties: AzureDevOpsConnectorStatsProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[AzureDevOpsConnectorStatsProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsConnectorStatsListResponse(Model):
        next_link: str
        value: list[AzureDevOpsConnectorStats]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AzureDevOpsConnectorStats]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsConnectorStatsProperties(Model):
        orgs_count: int
        projects_count: int
        provisioning_state: Union[str, ProvisioningState]
        repos_count: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                orgs_count: Optional[int] = ..., 
                projects_count: Optional[int] = ..., 
                repos_count: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsOrg(ProxyResource):
        id: str
        name: str
        properties: AzureDevOpsOrgProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[AzureDevOpsOrgProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsOrgListResponse(Model):
        next_link: str
        value: list[AzureDevOpsOrg]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AzureDevOpsOrg]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsOrgMetadata(Model):
        auto_discovery: Union[str, AutoDiscovery]
        name: str
        projects: list[AzureDevOpsProjectMetadata]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                name: Optional[str] = ..., 
                projects: Optional[List[AzureDevOpsProjectMetadata]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsOrgProperties(Model):
        auto_discovery: Union[str, AutoDiscovery]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsProject(ProxyResource):
        id: str
        name: str
        properties: AzureDevOpsProjectProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[AzureDevOpsProjectProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsProjectListResponse(Model):
        next_link: str
        value: list[AzureDevOpsProject]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AzureDevOpsProject]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsProjectMetadata(Model):
        auto_discovery: Union[str, AutoDiscovery]
        name: str
        repos: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                name: Optional[str] = ..., 
                repos: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsProjectProperties(Model):
        auto_discovery: Union[str, AutoDiscovery]
        org_name: str
        project_id: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auto_discovery: Optional[Union[str, AutoDiscovery]] = ..., 
                org_name: Optional[str] = ..., 
                project_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsRepo(ProxyResource):
        id: str
        name: str
        properties: AzureDevOpsRepoProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[AzureDevOpsRepoProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsRepoListResponse(Model):
        next_link: str
        value: list[AzureDevOpsRepo]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AzureDevOpsRepo]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.AzureDevOpsRepoProperties(Model):
        actionable_remediation: ActionableRemediation
        org_name: str
        project_name: str
        provisioning_state: Union[str, ProvisioningState]
        repo_id: str
        repo_url: str
        visibility: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                actionable_remediation: Optional[ActionableRemediation] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.securitydevops.models.ErrorAdditionalInfo(Model):
        info: JSON
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


    class azure.mgmt.securitydevops.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

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


    class azure.mgmt.securitydevops.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubConnector(TrackedResource):
        id: str
        location: str
        name: str
        properties: GitHubConnectorProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GitHubConnectorProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubConnectorListResponse(Model):
        next_link: str
        value: list[GitHubConnector]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[GitHubConnector]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubConnectorProperties(Model):
        code: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubConnectorStats(ProxyResource):
        id: str
        name: str
        properties: GitHubConnectorStatsProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[GitHubConnectorStatsProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubConnectorStatsListResponse(Model):
        next_link: str
        value: list[GitHubConnectorStats]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[GitHubConnectorStats]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubConnectorStatsProperties(Model):
        owners_count: int
        provisioning_state: Union[str, ProvisioningState]
        repos_count: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                owners_count: Optional[int] = ..., 
                repos_count: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubOwner(ProxyResource):
        id: str
        name: str
        properties: GitHubOwnerProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[GitHubOwnerProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubOwnerListResponse(Model):
        next_link: str
        value: list[GitHubOwner]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[GitHubOwner]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubOwnerProperties(Model):
        owner_url: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                owner_url: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubRepo(ProxyResource):
        id: str
        name: str
        properties: GitHubRepoProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[GitHubRepoProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubRepoListResponse(Model):
        next_link: str
        value: list[GitHubRepo]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[GitHubRepo]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubRepoProperties(Model):
        account_id: int
        owner_name: str
        provisioning_state: Union[str, ProvisioningState]
        repo_url: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                account_id: Optional[int] = ..., 
                owner_name: Optional[str] = ..., 
                repo_url: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.GitHubReposProperties(Model):
        account_id: int
        provisioning_state: Union[str, ProvisioningState]
        repo_name: str
        repo_url: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                account_id: Optional[int] = ..., 
                repo_name: Optional[str] = ..., 
                repo_url: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.securitydevops.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.securitydevops.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.securitydevops.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.securitydevops.models.ProxyResource(Resource):
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


    class azure.mgmt.securitydevops.models.Resource(Model):
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


    class azure.mgmt.securitydevops.models.RuleCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARTIFACTS = "Artifacts"
        CODE = "Code"
        CONTAINERS = "Containers"
        DEPENDENCIES = "Dependencies"
        IA_C = "IaC"
        SECRETS = "Secrets"


    class azure.mgmt.securitydevops.models.SystemData(Model):
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


    class azure.mgmt.securitydevops.models.TargetBranchConfiguration(Model):
        names: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                names: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.securitydevops.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


namespace azure.mgmt.securitydevops.operations

    class azure.mgmt.securitydevops.operations.AzureDevOpsConnectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_connector: AzureDevOpsConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsConnector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_connector: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsConnector]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_connector: Optional[AzureDevOpsConnector] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsConnector]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_connector: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsConnector]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureDevOpsConnector: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureDevOpsConnector]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureDevOpsConnector]: ...


    class azure.mgmt.securitydevops.operations.AzureDevOpsConnectorStatsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureDevOpsConnectorStatsListResponse: ...


    class azure.mgmt.securitydevops.operations.AzureDevOpsOrgOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_org: AzureDevOpsOrg, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsOrg]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_org: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsOrg]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_org: Optional[AzureDevOpsOrg] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsOrg]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_org: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsOrg]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureDevOpsOrg: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureDevOpsOrg]: ...


    class azure.mgmt.securitydevops.operations.AzureDevOpsProjectOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_project: AzureDevOpsProject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsProject]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_project: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsProject]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_project: Optional[AzureDevOpsProject] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsProject]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_project: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsProject]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureDevOpsProject: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureDevOpsProject]: ...


    class azure.mgmt.securitydevops.operations.AzureDevOpsRepoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_repo_name: str, 
                azure_dev_ops_repo: AzureDevOpsRepo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsRepo]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_repo_name: str, 
                azure_dev_ops_repo: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsRepo]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_repo_name: str, 
                azure_dev_ops_repo: Optional[AzureDevOpsRepo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsRepo]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_repo_name: str, 
                azure_dev_ops_repo: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureDevOpsRepo]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                azure_dev_ops_repo_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureDevOpsRepo: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                azure_dev_ops_org_name: str, 
                azure_dev_ops_project_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureDevOpsRepo]: ...

        @distributed_trace
        def list_by_connector(
                self, 
                resource_group_name: str, 
                azure_dev_ops_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureDevOpsRepo]: ...


    class azure.mgmt.securitydevops.operations.GitHubConnectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_connector: GitHubConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubConnector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_connector: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubConnector]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_connector: Optional[GitHubConnector] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubConnector]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_connector: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubConnector]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubConnector: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GitHubConnector]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GitHubConnector]: ...


    class azure.mgmt.securitydevops.operations.GitHubConnectorStatsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubConnectorStatsListResponse: ...


    class azure.mgmt.securitydevops.operations.GitHubOwnerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_owner: GitHubOwner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubOwner]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_owner: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubOwner]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_owner: Optional[GitHubOwner] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubOwner]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_owner: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubOwner]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubOwner: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GitHubOwner]: ...


    class azure.mgmt.securitydevops.operations.GitHubRepoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_repo_name: str, 
                git_hub_repo: GitHubRepo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubRepo]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_repo_name: str, 
                git_hub_repo: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubRepo]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_repo_name: str, 
                git_hub_repo: Optional[GitHubRepo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubRepo]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_repo_name: str, 
                git_hub_repo: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GitHubRepo]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                git_hub_repo_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubRepo: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                git_hub_owner_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GitHubRepo]: ...

        @distributed_trace
        def list_by_connector(
                self, 
                resource_group_name: str, 
                git_hub_connector_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GitHubRepo]: ...


    class azure.mgmt.securitydevops.operations.Operations:

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


```