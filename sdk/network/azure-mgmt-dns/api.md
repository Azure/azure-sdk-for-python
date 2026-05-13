```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.dns

    class azure.mgmt.dns.DnsManagementClient: implements ContextManager 
        dns_resource_reference: DnsResourceReferenceOperations
        record_sets: RecordSetsOperations
        zones: ZonesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.dns.aio

    class azure.mgmt.dns.aio.DnsManagementClient: implements AsyncContextManager 
        dns_resource_reference: DnsResourceReferenceOperations
        record_sets: RecordSetsOperations
        zones: ZonesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.dns.aio.operations

    class azure.mgmt.dns.aio.operations.DnsResourceReferenceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def get_by_target_resources(
                self, 
                parameters: DnsResourceReferenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DnsResourceReferenceResult: ...

        @overload
        async def get_by_target_resources(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DnsResourceReferenceResult: ...


    class azure.mgmt.dns.aio.operations.RecordSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
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
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
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
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                if_match: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                **kwargs: Any
            ) -> RecordSet: ...

        @distributed_trace
        def list_all_by_dns_zone(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                top: Optional[int] = None, 
                record_set_name_suffix: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecordSet]: ...

        @distributed_trace
        def list_by_dns_zone(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                top: Optional[int] = None, 
                recordsetnamesuffix: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecordSet]: ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                record_type: Union[str, RecordType], 
                top: Optional[int] = None, 
                recordsetnamesuffix: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecordSet]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
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
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecordSet: ...


    class azure.mgmt.dns.aio.operations.ZonesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                if_match: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: Zone, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Zone: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                **kwargs: Any
            ) -> Zone: ...

        @distributed_trace
        def list(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Zone]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[Zone]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: ZoneUpdate, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Zone: ...


namespace azure.mgmt.dns.models

    class azure.mgmt.dns.models.ARecord(Model):
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


    class azure.mgmt.dns.models.AaaaRecord(Model):
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


    class azure.mgmt.dns.models.CaaRecord(Model):
        flags: int
        tag: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                flags: Optional[int] = ..., 
                tag: Optional[str] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.dns.models.CloudErrorBody(Model):
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


    class azure.mgmt.dns.models.CnameRecord(Model):
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


    class azure.mgmt.dns.models.DnsResourceReference(Model):
        dns_resources: list[SubResource]
        target_resource: SubResource

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dns_resources: Optional[List[SubResource]] = ..., 
                target_resource: Optional[SubResource] = ..., 
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


    class azure.mgmt.dns.models.DnsResourceReferenceRequest(Model):
        target_resources: list[SubResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target_resources: Optional[List[SubResource]] = ..., 
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


    class azure.mgmt.dns.models.DnsResourceReferenceResult(Model):
        dns_resource_references: list[DnsResourceReference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dns_resource_references: Optional[List[DnsResourceReference]] = ..., 
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


    class azure.mgmt.dns.models.MxRecord(Model):
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


    class azure.mgmt.dns.models.NsRecord(Model):
        nsdname: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                nsdname: Optional[str] = ..., 
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


    class azure.mgmt.dns.models.PtrRecord(Model):
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


    class azure.mgmt.dns.models.RecordSet(Model):
        a_records: list[ARecord]
        aaaa_records: list[AaaaRecord]
        caa_records: list[CaaRecord]
        cname_record: CnameRecord
        etag: str
        fqdn: str
        id: str
        metadata: dict[str, str]
        mx_records: list[MxRecord]
        name: str
        ns_records: list[NsRecord]
        provisioning_state: str
        ptr_records: list[PtrRecord]
        soa_record: SoaRecord
        srv_records: list[SrvRecord]
        target_resource: SubResource
        ttl: int
        txt_records: list[TxtRecord]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                a_records: Optional[List[ARecord]] = ..., 
                aaaa_records: Optional[List[AaaaRecord]] = ..., 
                caa_records: Optional[List[CaaRecord]] = ..., 
                cname_record: Optional[CnameRecord] = ..., 
                etag: Optional[str] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                mx_records: Optional[List[MxRecord]] = ..., 
                ns_records: Optional[List[NsRecord]] = ..., 
                ptr_records: Optional[List[PtrRecord]] = ..., 
                soa_record: Optional[SoaRecord] = ..., 
                srv_records: Optional[List[SrvRecord]] = ..., 
                target_resource: Optional[SubResource] = ..., 
                ttl: Optional[int] = ..., 
                txt_records: Optional[List[TxtRecord]] = ..., 
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


    class azure.mgmt.dns.models.RecordSetListResult(Model):
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


    class azure.mgmt.dns.models.RecordSetUpdateParameters(Model):
        record_set: RecordSet

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                record_set: Optional[RecordSet] = ..., 
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


    class azure.mgmt.dns.models.RecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A = "A"
        AAAA = "AAAA"
        CAA = "CAA"
        CNAME = "CNAME"
        MX = "MX"
        NS = "NS"
        PTR = "PTR"
        SOA = "SOA"
        SRV = "SRV"
        TXT = "TXT"


    class azure.mgmt.dns.models.Resource(Model):
        id: str
        location: str
        name: str
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


    class azure.mgmt.dns.models.SoaRecord(Model):
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


    class azure.mgmt.dns.models.SrvRecord(Model):
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


    class azure.mgmt.dns.models.SubResource(Model):
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


    class azure.mgmt.dns.models.TxtRecord(Model):
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


    class azure.mgmt.dns.models.Zone(Resource):
        etag: str
        id: str
        location: str
        max_number_of_record_sets: int
        max_number_of_records_per_record_set: int
        name: str
        name_servers: list[str]
        number_of_record_sets: int
        registration_virtual_networks: list[SubResource]
        resolution_virtual_networks: list[SubResource]
        tags: dict[str, str]
        type: str
        zone_type: Union[str, ZoneType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str, 
                registration_virtual_networks: Optional[List[SubResource]] = ..., 
                resolution_virtual_networks: Optional[List[SubResource]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                zone_type: Union[str, ZoneType] = "Public", 
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


    class azure.mgmt.dns.models.ZoneListResult(Model):
        next_link: str
        value: list[Zone]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Zone]] = ..., 
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


    class azure.mgmt.dns.models.ZoneType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.dns.models.ZoneUpdate(Model):
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


namespace azure.mgmt.dns.operations

    class azure.mgmt.dns.operations.DnsResourceReferenceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def get_by_target_resources(
                self, 
                parameters: DnsResourceReferenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DnsResourceReferenceResult: ...

        @overload
        def get_by_target_resources(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DnsResourceReferenceResult: ...


    class azure.mgmt.dns.operations.RecordSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
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
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
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
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                if_match: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                **kwargs: Any
            ) -> RecordSet: ...

        @distributed_trace
        def list_all_by_dns_zone(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                top: Optional[int] = None, 
                record_set_name_suffix: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[RecordSet]: ...

        @distributed_trace
        def list_by_dns_zone(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                top: Optional[int] = None, 
                recordsetnamesuffix: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[RecordSet]: ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                record_type: Union[str, RecordType], 
                top: Optional[int] = None, 
                recordsetnamesuffix: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[RecordSet]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
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
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecordSet: ...


    class azure.mgmt.dns.operations.ZonesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                if_match: Optional[str] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: Zone, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Zone: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                **kwargs: Any
            ) -> Zone: ...

        @distributed_trace
        def list(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Zone]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[Zone]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: ZoneUpdate, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: IO[bytes], 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Zone: ...


```