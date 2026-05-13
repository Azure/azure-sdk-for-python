```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.resource.privatelinks

    class azure.mgmt.resource.privatelinks.ResourcePrivateLinkClient: implements ContextManager 
        private_link_association: PrivateLinkAssociationOperations
        resource_management_private_link: ResourceManagementPrivateLinkOperations

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


namespace azure.mgmt.resource.privatelinks.aio

    class azure.mgmt.resource.privatelinks.aio.ResourcePrivateLinkClient: implements AsyncContextManager 
        private_link_association: PrivateLinkAssociationOperations
        resource_management_private_link: ResourceManagementPrivateLinkOperations

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


namespace azure.mgmt.resource.privatelinks.aio.operations

    class azure.mgmt.resource.privatelinks.aio.operations.PrivateLinkAssociationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                group_id: str, 
                pla_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                group_id: str, 
                pla_id: str, 
                **kwargs: Any
            ) -> PrivateLinkAssociation: ...

        @distributed_trace_async
        async def list(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> PrivateLinkAssociationGetResult: ...

        @overload
        async def put(
                self, 
                group_id: str, 
                pla_id: str, 
                parameters: PrivateLinkAssociationObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkAssociation: ...

        @overload
        async def put(
                self, 
                group_id: str, 
                pla_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkAssociation: ...


    class azure.mgmt.resource.privatelinks.aio.operations.ResourceManagementPrivateLinkOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                rmpl_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                rmpl_name: str, 
                **kwargs: Any
            ) -> ResourceManagementPrivateLink: ...

        @distributed_trace_async
        async def list(self, **kwargs: Any) -> ResourceManagementPrivateLinkListResult: ...

        @distributed_trace_async
        async def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ResourceManagementPrivateLinkListResult: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                rmpl_name: str, 
                parameters: ResourceManagementPrivateLinkLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceManagementPrivateLink: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                rmpl_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceManagementPrivateLink: ...


namespace azure.mgmt.resource.privatelinks.models

    class azure.mgmt.resource.privatelinks.models.ErrorAdditionalInfo(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.privatelinks.models.ErrorResponse(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.privatelinks.models.PrivateLinkAssociation(Model):
        id: str
        name: str
        properties: PrivateLinkAssociationPropertiesExpanded
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkAssociationPropertiesExpanded] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.privatelinks.models.PrivateLinkAssociationGetResult(Model):
        value: list[PrivateLinkAssociation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkAssociation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.privatelinks.models.PrivateLinkAssociationObject(Model):
        properties: PrivateLinkAssociationProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkAssociationProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.privatelinks.models.PrivateLinkAssociationProperties(Model):
        private_link: str
        public_network_access: Union[str, PublicNetworkAccessOptions]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_link: Optional[str] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccessOptions]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.privatelinks.models.PrivateLinkAssociationPropertiesExpanded(Model):
        private_link: str
        public_network_access: Union[str, PublicNetworkAccessOptions]
        scope: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_link: Optional[str] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccessOptions]] = ..., 
                scope: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.privatelinks.models.PublicNetworkAccessOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.resource.privatelinks.models.ResourceManagementPrivateLink(Model):
        id: str
        location: str
        name: str
        properties: ResourceManagementPrivateLinkEndpointConnections
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ResourceManagementPrivateLinkEndpointConnections] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.privatelinks.models.ResourceManagementPrivateLinkEndpointConnections(Model):
        private_endpoint_connections: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint_connections: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.privatelinks.models.ResourceManagementPrivateLinkListResult(Model):
        value: list[ResourceManagementPrivateLink]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[ResourceManagementPrivateLink]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.privatelinks.models.ResourceManagementPrivateLinkLocation(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.mgmt.resource.privatelinks.operations

    class azure.mgmt.resource.privatelinks.operations.PrivateLinkAssociationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                group_id: str, 
                pla_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                group_id: str, 
                pla_id: str, 
                **kwargs: Any
            ) -> PrivateLinkAssociation: ...

        @distributed_trace
        def list(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> PrivateLinkAssociationGetResult: ...

        @overload
        def put(
                self, 
                group_id: str, 
                pla_id: str, 
                parameters: PrivateLinkAssociationObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkAssociation: ...

        @overload
        def put(
                self, 
                group_id: str, 
                pla_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkAssociation: ...


    class azure.mgmt.resource.privatelinks.operations.ResourceManagementPrivateLinkOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                rmpl_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                rmpl_name: str, 
                **kwargs: Any
            ) -> ResourceManagementPrivateLink: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ResourceManagementPrivateLinkListResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ResourceManagementPrivateLinkListResult: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                rmpl_name: str, 
                parameters: ResourceManagementPrivateLinkLocation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceManagementPrivateLink: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                rmpl_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceManagementPrivateLink: ...


```