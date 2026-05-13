```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.resource.templatespecs

    class azure.mgmt.resource.templatespecs.TemplateSpecsClient: implements ContextManager 
        template_spec_versions: TemplateSpecVersionsOperations
        template_specs: TemplateSpecsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.resource.templatespecs.aio

    class azure.mgmt.resource.templatespecs.aio.TemplateSpecsClient: implements AsyncContextManager 
        template_spec_versions: TemplateSpecVersionsOperations
        template_specs: TemplateSpecsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.resource.templatespecs.aio.operations

    class azure.mgmt.resource.templatespecs.aio.operations.TemplateSpecVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                template_spec_version_model: TemplateSpecVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpecVersion: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                template_spec_version_model: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpecVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                **kwargs: Any
            ) -> TemplateSpecVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TemplateSpecVersion]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                template_spec_version_update_model: Optional[TemplateSpecVersionUpdateModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpecVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                template_spec_version_update_model: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpecVersion: ...


    class azure.mgmt.resource.templatespecs.aio.operations.TemplateSpecsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec: TemplateSpec, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpec: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpec: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                expand: Optional[Union[str, TemplateSpecExpandKind]] = None, 
                **kwargs: Any
            ) -> TemplateSpec: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: Optional[Union[str, TemplateSpecExpandKind]] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[TemplateSpec]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                expand: Optional[Union[str, TemplateSpecExpandKind]] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[TemplateSpec]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec: Optional[TemplateSpecUpdateModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpec: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpec: ...


namespace azure.mgmt.resource.templatespecs.models

    class azure.mgmt.resource.templatespecs.models.AzureResourceBase(Model):
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


    class azure.mgmt.resource.templatespecs.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resource.templatespecs.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.resource.templatespecs.models.ErrorResponse(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorResponse]
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


    class azure.mgmt.resource.templatespecs.models.LinkedTemplateArtifact(Model):
        path: str
        template: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                path: str, 
                template: JSON, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.templatespecs.models.SystemData(Model):
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


    class azure.mgmt.resource.templatespecs.models.TemplateSpec(AzureResourceBase):
        description: str
        display_name: str
        id: str
        location: str
        metadata: JSON
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        versions: dict[str, TemplateSpecVersionInfo]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                location: str, 
                metadata: Optional[JSON] = ..., 
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


    class azure.mgmt.resource.templatespecs.models.TemplateSpecExpandKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VERSIONS = "versions"


    class azure.mgmt.resource.templatespecs.models.TemplateSpecUpdateModel(AzureResourceBase):
        id: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

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


    class azure.mgmt.resource.templatespecs.models.TemplateSpecVersion(AzureResourceBase):
        description: str
        id: str
        linked_templates: list[LinkedTemplateArtifact]
        location: str
        main_template: JSON
        metadata: JSON
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        ui_form_definition: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                linked_templates: Optional[List[LinkedTemplateArtifact]] = ..., 
                location: str, 
                main_template: Optional[JSON] = ..., 
                metadata: Optional[JSON] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                ui_form_definition: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.templatespecs.models.TemplateSpecVersionInfo(Model):
        description: str
        time_created: datetime
        time_modified: datetime

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


    class azure.mgmt.resource.templatespecs.models.TemplateSpecVersionUpdateModel(AzureResourceBase):
        id: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

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


    class azure.mgmt.resource.templatespecs.models.TemplateSpecVersionsListResult(Model):
        next_link: str
        value: list[TemplateSpecVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[TemplateSpecVersion]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.templatespecs.models.TemplateSpecsError(Model):
        error: ErrorResponse

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.templatespecs.models.TemplateSpecsListResult(Model):
        next_link: str
        value: list[TemplateSpec]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[TemplateSpec]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.mgmt.resource.templatespecs.operations

    class azure.mgmt.resource.templatespecs.operations.TemplateSpecVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                template_spec_version_model: TemplateSpecVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpecVersion: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                template_spec_version_model: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpecVersion: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                **kwargs: Any
            ) -> TemplateSpecVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TemplateSpecVersion]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                template_spec_version_update_model: Optional[TemplateSpecVersionUpdateModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpecVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec_version: str, 
                template_spec_version_update_model: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpecVersion: ...


    class azure.mgmt.resource.templatespecs.operations.TemplateSpecsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec: TemplateSpec, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpec: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpec: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                expand: Optional[Union[str, TemplateSpecExpandKind]] = None, 
                **kwargs: Any
            ) -> TemplateSpec: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                expand: Optional[Union[str, TemplateSpecExpandKind]] = None, 
                **kwargs: Any
            ) -> ItemPaged[TemplateSpec]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                expand: Optional[Union[str, TemplateSpecExpandKind]] = None, 
                **kwargs: Any
            ) -> ItemPaged[TemplateSpec]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec: Optional[TemplateSpecUpdateModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpec: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                template_spec_name: str, 
                template_spec: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TemplateSpec: ...


```