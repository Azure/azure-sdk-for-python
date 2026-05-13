```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.devhub

    class azure.mgmt.devhub.DevHubMgmtClient(DevHubMgmtClientOperationsMixin): implements ContextManager 
        operations: Operations
        workflow: WorkflowOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def generate_preview_artifacts(
                self, 
                location: str, 
                parameters: ArtifactGenerationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @overload
        def generate_preview_artifacts(
                self, 
                location: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @overload
        def git_hub_o_auth(
                self, 
                location: str, 
                parameters: Optional[GitHubOAuthCallRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GitHubOAuthInfoResponse: ...

        @overload
        def git_hub_o_auth(
                self, 
                location: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GitHubOAuthInfoResponse: ...

        @distributed_trace
        def git_hub_o_auth_callback(
                self, 
                location: str, 
                code: str, 
                state: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubOAuthResponse: ...

        @distributed_trace
        def list_git_hub_o_auth(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubOAuthListResponse: ...


namespace azure.mgmt.devhub.aio

    class azure.mgmt.devhub.aio.DevHubMgmtClient(DevHubMgmtClientOperationsMixin): implements AsyncContextManager 
        operations: Operations
        workflow: WorkflowOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def generate_preview_artifacts(
                self, 
                location: str, 
                parameters: ArtifactGenerationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @overload
        async def generate_preview_artifacts(
                self, 
                location: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @overload
        async def git_hub_o_auth(
                self, 
                location: str, 
                parameters: Optional[GitHubOAuthCallRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GitHubOAuthInfoResponse: ...

        @overload
        async def git_hub_o_auth(
                self, 
                location: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GitHubOAuthInfoResponse: ...

        @distributed_trace_async
        async def git_hub_o_auth_callback(
                self, 
                location: str, 
                code: str, 
                state: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubOAuthResponse: ...

        @distributed_trace_async
        async def list_git_hub_o_auth(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubOAuthListResponse: ...


namespace azure.mgmt.devhub.aio.operations

    class azure.mgmt.devhub.aio.operations.DevHubMgmtClientOperationsMixin(DevHubMgmtClientMixinABC):

        @overload
        async def generate_preview_artifacts(
                self, 
                location: str, 
                parameters: ArtifactGenerationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @overload
        async def generate_preview_artifacts(
                self, 
                location: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @overload
        async def git_hub_o_auth(
                self, 
                location: str, 
                parameters: Optional[GitHubOAuthCallRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GitHubOAuthInfoResponse: ...

        @overload
        async def git_hub_o_auth(
                self, 
                location: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GitHubOAuthInfoResponse: ...

        @distributed_trace_async
        async def git_hub_o_auth_callback(
                self, 
                location: str, 
                code: str, 
                state: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubOAuthResponse: ...

        @distributed_trace_async
        async def list_git_hub_o_auth(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubOAuthListResponse: ...


    class azure.mgmt.devhub.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationListResult: ...


    class azure.mgmt.devhub.aio.operations.WorkflowOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[DeleteWorkflowResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Workflow]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                managed_cluster_resource: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Workflow]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...


namespace azure.mgmt.devhub.models

    class azure.mgmt.devhub.models.ACR(Model):
        acr_registry_name: str
        acr_repository_name: str
        acr_resource_group: str
        acr_subscription_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                acr_registry_name: Optional[str] = ..., 
                acr_repository_name: Optional[str] = ..., 
                acr_resource_group: Optional[str] = ..., 
                acr_subscription_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.devhub.models.ArtifactGenerationProperties(Model):
        app_name: str
        builder_version: str
        dockerfile_generation_mode: Union[str, DockerfileGenerationMode]
        dockerfile_output_directory: str
        generation_language: Union[str, GenerationLanguage]
        image_name: str
        image_tag: str
        language_version: str
        manifest_generation_mode: Union[str, ManifestGenerationMode]
        manifest_output_directory: str
        manifest_type: Union[str, GenerationManifestType]
        namespace: str
        port: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_name: Optional[str] = ..., 
                builder_version: Optional[str] = ..., 
                dockerfile_generation_mode: Optional[Union[str, DockerfileGenerationMode]] = ..., 
                dockerfile_output_directory: Optional[str] = ..., 
                generation_language: Optional[Union[str, GenerationLanguage]] = ..., 
                image_name: Optional[str] = ..., 
                image_tag: Optional[str] = ..., 
                language_version: Optional[str] = ..., 
                manifest_generation_mode: Optional[Union[str, ManifestGenerationMode]] = ..., 
                manifest_output_directory: Optional[str] = ..., 
                manifest_type: Optional[Union[str, GenerationManifestType]] = ..., 
                namespace: Optional[str] = ..., 
                port: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.AuthorizationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTHORIZED = "Authorized"
        ERROR = "Error"
        NOT_FOUND = "NotFound"


    class azure.mgmt.devhub.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.devhub.models.DeleteWorkflowResponse(Model):
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                status: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.DeploymentProperties(Model):
        helm_chart_path: str
        helm_values: str
        kube_manifest_locations: list[str]
        manifest_type: Union[str, ManifestType]
        overrides: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                helm_chart_path: Optional[str] = ..., 
                helm_values: Optional[str] = ..., 
                kube_manifest_locations: Optional[List[str]] = ..., 
                manifest_type: Optional[Union[str, ManifestType]] = ..., 
                overrides: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.DockerfileGenerationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.devhub.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.ErrorDetail(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.ErrorResponse(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.GenerationLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOJURE = "clojure"
        CSHARP = "csharp"
        ERLANG = "erlang"
        GO = "go"
        GOMODULE = "gomodule"
        GRADLE = "gradle"
        JAVA = "java"
        JAVASCRIPT = "javascript"
        PHP = "php"
        PYTHON = "python"
        RUBY = "ruby"
        RUST = "rust"
        SWIFT = "swift"


    class azure.mgmt.devhub.models.GenerationManifestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HELM = "helm"
        KUBE = "kube"


    class azure.mgmt.devhub.models.GitHubOAuthCallRequest(Model):
        redirect_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                redirect_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.GitHubOAuthInfoResponse(Model):
        auth_url: str
        token: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_url: Optional[str] = ..., 
                token: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.GitHubOAuthListResponse(Model):
        value: list[GitHubOAuthResponse]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[GitHubOAuthResponse]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.GitHubOAuthResponse(ProxyResource):
        id: str
        name: str
        system_data: SystemData
        type: str
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                username: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.GitHubWorkflowProfileOidcCredentials(Model):
        azure_client_id: str
        azure_tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_client_id: Optional[str] = ..., 
                azure_tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.ManifestGenerationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.devhub.models.ManifestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HELM = "helm"
        KUBE = "kube"


    class azure.mgmt.devhub.models.Operation(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.OperationDisplay(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.devhub.models.ProxyResource(Resource):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.PullRequestStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MERGED = "merged"
        REMOVED = "removed"
        SUBMITTED = "submitted"
        UNKNOWN = "unknown"


    class azure.mgmt.devhub.models.Resource(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.SystemData(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.TagsObject(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.TrackedResource(Resource):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.Workflow(TrackedResource):
        acr: azure.mgmt.devhub.models.ACR
        aks_resource_id: str
        app_name: str
        auth_status: Union[str, AuthorizationStatus]
        branch_name: str
        builder_version: str
        deployment_properties: DeploymentProperties
        docker_build_context: str
        dockerfile: str
        dockerfile_generation_mode: Union[str, DockerfileGenerationMode]
        dockerfile_output_directory: str
        generation_language: Union[str, GenerationLanguage]
        id: str
        image_name: str
        image_tag: str
        language_version: str
        last_workflow_run: WorkflowRun
        location: str
        manifest_generation_mode: Union[str, ManifestGenerationMode]
        manifest_output_directory: str
        manifest_type: Union[str, GenerationManifestType]
        name: str
        namespace_properties_artifact_generation_properties_namespace: str
        namespace_properties_github_workflow_profile_namespace: str
        oidc_credentials: GitHubWorkflowProfileOidcCredentials
        port: str
        pr_status: Union[str, PullRequestStatus]
        pr_url: str
        pull_number: int
        repository_name: str
        repository_owner: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                acr: Optional[_models.ACR] = ..., 
                aks_resource_id: Optional[str] = ..., 
                app_name: Optional[str] = ..., 
                branch_name: Optional[str] = ..., 
                builder_version: Optional[str] = ..., 
                deployment_properties: Optional[DeploymentProperties] = ..., 
                docker_build_context: Optional[str] = ..., 
                dockerfile: Optional[str] = ..., 
                dockerfile_generation_mode: Optional[Union[str, DockerfileGenerationMode]] = ..., 
                dockerfile_output_directory: Optional[str] = ..., 
                generation_language: Optional[Union[str, GenerationLanguage]] = ..., 
                image_name: Optional[str] = ..., 
                image_tag: Optional[str] = ..., 
                language_version: Optional[str] = ..., 
                last_workflow_run: Optional[WorkflowRun] = ..., 
                location: str, 
                manifest_generation_mode: Optional[Union[str, ManifestGenerationMode]] = ..., 
                manifest_output_directory: Optional[str] = ..., 
                manifest_type: Optional[Union[str, GenerationManifestType]] = ..., 
                namespace_properties_artifact_generation_properties_namespace: Optional[str] = ..., 
                namespace_properties_github_workflow_profile_namespace: Optional[str] = ..., 
                oidc_credentials: Optional[GitHubWorkflowProfileOidcCredentials] = ..., 
                port: Optional[str] = ..., 
                repository_name: Optional[str] = ..., 
                repository_owner: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.WorkflowListResult(Model):
        next_link: str
        value: list[Workflow]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Workflow]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.WorkflowRun(Model):
        last_run_at: datetime
        succeeded: bool
        workflow_run_status: Union[str, WorkflowRunStatus]
        workflow_run_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                workflow_run_status: Optional[Union[str, WorkflowRunStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.devhub.models.WorkflowRunStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        INPROGRESS = "inprogress"
        QUEUED = "queued"


namespace azure.mgmt.devhub.operations

    class azure.mgmt.devhub.operations.DevHubMgmtClientOperationsMixin(DevHubMgmtClientMixinABC):

        @overload
        def generate_preview_artifacts(
                self, 
                location: str, 
                parameters: ArtifactGenerationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @overload
        def generate_preview_artifacts(
                self, 
                location: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Dict[str, str]: ...

        @overload
        def git_hub_o_auth(
                self, 
                location: str, 
                parameters: Optional[GitHubOAuthCallRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GitHubOAuthInfoResponse: ...

        @overload
        def git_hub_o_auth(
                self, 
                location: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GitHubOAuthInfoResponse: ...

        @distributed_trace
        def git_hub_o_auth_callback(
                self, 
                location: str, 
                code: str, 
                state: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubOAuthResponse: ...

        @distributed_trace
        def list_git_hub_o_auth(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GitHubOAuthListResponse: ...


    class azure.mgmt.devhub.operations.Operations:

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
            ) -> OperationListResult: ...


    class azure.mgmt.devhub.operations.WorkflowOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[DeleteWorkflowResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Workflow]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                managed_cluster_resource: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Workflow]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...


```