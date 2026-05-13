```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.privatedns

    class azure.mgmt.privatedns.PrivateDnsManagementClient: implements ContextManager 
        private_zones: PrivateZonesOperations
        record_sets: RecordSetsOperations
        virtual_network_links: VirtualNetworkLinksOperations

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


namespace azure.mgmt.privatedns.aio

    class azure.mgmt.privatedns.aio.PrivateDnsManagementClient: implements AsyncContextManager 
        private_zones: PrivateZonesOperations
        record_sets: RecordSetsOperations
        virtual_network_links: VirtualNetworkLinksOperations

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


namespace azure.mgmt.privatedns.aio.operations

    class azure.mgmt.privatedns.aio.operations.PrivateZonesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateZone]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateZone]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                if_match: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateZone]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateZone]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                **kwargs: Any
            ) -> PrivateZone: ...

        @distributed_trace
        def list(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateZone]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateZone]: ...


    class azure.mgmt.privatedns.aio.operations.RecordSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                parameters: RecordSet, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecordSet: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecordSet: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                if_match: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                **kwargs: Any
            ) -> RecordSet: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                top: Optional[int] = None, 
                recordsetnamesuffix: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[RecordSet]: ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                top: Optional[int] = None, 
                recordsetnamesuffix: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[RecordSet]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                parameters: RecordSet, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecordSet: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecordSet: ...


    class azure.mgmt.privatedns.aio.operations.VirtualNetworkLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                if_match: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                **kwargs: Any
            ) -> VirtualNetworkLink: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[VirtualNetworkLink]: ...


namespace azure.mgmt.privatedns.models

    class azure.mgmt.privatedns.models.ARecord(Model):
        ipv4_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ipv4_address: Optional[str] = ..., 
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


    class azure.mgmt.privatedns.models.AaaaRecord(Model):
        ipv6_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ipv6_address: Optional[str] = ..., 
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


    class azure.mgmt.privatedns.models.CloudErrorBody(Model):
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
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


    class azure.mgmt.privatedns.models.CnameRecord(Model):
        cname: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cname: Optional[str] = ..., 
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


    class azure.mgmt.privatedns.models.MxRecord(Model):
        exchange: str
        preference: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                exchange: Optional[str] = ..., 
                preference: Optional[int] = ..., 
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


    class azure.mgmt.privatedns.models.PrivateZone(TrackedResource):
        etag: str
        id: str
        internal_id: str
        location: str
        max_number_of_record_sets: int
        max_number_of_virtual_network_links: int
        max_number_of_virtual_network_links_with_registration: int
        name: str
        number_of_record_sets: int
        number_of_virtual_network_links: int
        number_of_virtual_network_links_with_registration: int
        provisioning_state: Union[str, ProvisioningState]
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
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


    class azure.mgmt.privatedns.models.PrivateZoneListResult(Model):
        next_link: str
        value: list[PrivateZone]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateZone]] = ..., 
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


    class azure.mgmt.privatedns.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.privatedns.models.ProxyResource(Resource):
        id: str
        name: str
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


    class azure.mgmt.privatedns.models.PtrRecord(Model):
        ptrdname: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ptrdname: Optional[str] = ..., 
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


    class azure.mgmt.privatedns.models.RecordSet(ProxyResource):
        a_records: list[ARecord]
        aaaa_records: list[AaaaRecord]
        cname_record: CnameRecord
        etag: str
        fqdn: str
        id: str
        is_auto_registered: bool
        metadata: dict[str, str]
        mx_records: list[MxRecord]
        name: str
        ptr_records: list[PtrRecord]
        soa_record: SoaRecord
        srv_records: list[SrvRecord]
        ttl: int
        txt_records: list[TxtRecord]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                a_records: Optional[List[ARecord]] = ..., 
                aaaa_records: Optional[List[AaaaRecord]] = ..., 
                cname_record: Optional[CnameRecord] = ..., 
                etag: Optional[str] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                mx_records: Optional[List[MxRecord]] = ..., 
                ptr_records: Optional[List[PtrRecord]] = ..., 
                soa_record: Optional[SoaRecord] = ..., 
                srv_records: Optional[List[SrvRecord]] = ..., 
                ttl: Optional[int] = ..., 
                txt_records: Optional[List[TxtRecord]] = ..., 
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


    class azure.mgmt.privatedns.models.RecordSetListResult(Model):
        next_link: str
        value: list[RecordSet]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[RecordSet]] = ..., 
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


    class azure.mgmt.privatedns.models.RecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A = "A"
        AAAA = "AAAA"
        CNAME = "CNAME"
        MX = "MX"
        PTR = "PTR"
        SOA = "SOA"
        SRV = "SRV"
        TXT = "TXT"


    class azure.mgmt.privatedns.models.ResolutionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        NX_DOMAIN_REDIRECT = "NxDomainRedirect"


    class azure.mgmt.privatedns.models.Resource(Model):
        id: str
        name: str
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


    class azure.mgmt.privatedns.models.SoaRecord(Model):
        email: str
        expire_time: int
        host: str
        minimum_ttl: int
        refresh_time: int
        retry_time: int
        serial_number: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                expire_time: Optional[int] = ..., 
                host: Optional[str] = ..., 
                minimum_ttl: Optional[int] = ..., 
                refresh_time: Optional[int] = ..., 
                retry_time: Optional[int] = ..., 
                serial_number: Optional[int] = ..., 
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


    class azure.mgmt.privatedns.models.SrvRecord(Model):
        port: int
        priority: int
        target: str
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                port: Optional[int] = ..., 
                priority: Optional[int] = ..., 
                target: Optional[str] = ..., 
                weight: Optional[int] = ..., 
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


    class azure.mgmt.privatedns.models.SubResource(Model):
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


    class azure.mgmt.privatedns.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
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


    class azure.mgmt.privatedns.models.TxtRecord(Model):
        value: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[str]] = ..., 
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


    class azure.mgmt.privatedns.models.VirtualNetworkLink(TrackedResource):
        etag: str
        id: str
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        registration_enabled: bool
        resolution_policy: Union[str, ResolutionPolicy]
        tags: dict[str, str]
        type: str
        virtual_network: SubResource
        virtual_network_link_state: Union[str, VirtualNetworkLinkState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                registration_enabled: Optional[bool] = ..., 
                resolution_policy: Optional[Union[str, ResolutionPolicy]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                virtual_network: Optional[SubResource] = ..., 
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


    class azure.mgmt.privatedns.models.VirtualNetworkLinkListResult(Model):
        next_link: str
        value: list[VirtualNetworkLink]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[VirtualNetworkLink]] = ..., 
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


    class azure.mgmt.privatedns.models.VirtualNetworkLinkState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        IN_PROGRESS = "InProgress"


namespace azure.mgmt.privatedns.operations

    class azure.mgmt.privatedns.operations.PrivateZonesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateZone]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateZone]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                if_match: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateZone]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateZone]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                **kwargs: Any
            ) -> PrivateZone: ...

        @distributed_trace
        def list(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[PrivateZone]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[PrivateZone]: ...


    class azure.mgmt.privatedns.operations.RecordSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                parameters: RecordSet, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecordSet: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecordSet: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                if_match: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                **kwargs: Any
            ) -> RecordSet: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                top: Optional[int] = None, 
                recordsetnamesuffix: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[RecordSet]: ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                top: Optional[int] = None, 
                recordsetnamesuffix: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[RecordSet]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                parameters: RecordSet, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecordSet: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecordSet: ...


    class azure.mgmt.privatedns.operations.VirtualNetworkLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                if_match: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                **kwargs: Any
            ) -> VirtualNetworkLink: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[VirtualNetworkLink]: ...


```