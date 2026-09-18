```py
namespace azure.mgmt.dns

    class azure.mgmt.dns.DnsManagementClient: implements ContextManager 
        dns_resource_reference: DnsResourceReferenceOperations
        dnssec_configs: DnssecConfigsOperations
        record_sets: RecordSetsOperations
        zones: ZonesOperations

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


namespace azure.mgmt.dns.aio

    class azure.mgmt.dns.aio.DnsManagementClient: implements AsyncContextManager 
        dns_resource_reference: DnsResourceReferenceOperations
        dnssec_configs: DnssecConfigsOperations
        record_sets: RecordSetsOperations
        zones: ZonesOperations

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


    class azure.mgmt.dns.aio.operations.DnssecConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DnssecConfig]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                **kwargs: Any
            ) -> DnssecConfig: ...

        @distributed_trace
        def list_by_dns_zone(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DnssecConfig]: ...


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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RecordSet: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                parameters: RecordSet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RecordSet: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                record_set_name_suffix: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RecordSet]: ...

        @distributed_trace
        def list_by_dns_zone(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                *, 
                recordsetnamesuffix: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RecordSet]: ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                record_type: Union[str, RecordType], 
                *, 
                recordsetnamesuffix: Optional[str] = ..., 
                top: Optional[int] = ..., 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RecordSet: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                parameters: RecordSet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: Zone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: Zone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Zone]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Zone]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: ZoneUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: ZoneUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Zone: ...


namespace azure.mgmt.dns.models

    class azure.mgmt.dns.models.ARecord(_Model):
        ipv4_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.AaaaRecord(_Model):
        ipv6_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ipv6_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.CaaRecord(_Model):
        flags: Optional[int]
        tag: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                flags: Optional[int] = ..., 
                tag: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.CloudErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[CloudErrorBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.CnameRecord(_Model):
        cname: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cname: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.dns.models.DelegationSignerInfo(_Model):
        digest_algorithm_type: Optional[int]
        digest_value: Optional[str]
        record: Optional[str]


    class azure.mgmt.dns.models.Digest(_Model):
        algorithm_type: Optional[int]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                algorithm_type: Optional[int] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.DnsResourceReference(_Model):
        dns_resources: Optional[list[SubResource]]
        target_resource: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                dns_resources: Optional[list[SubResource]] = ..., 
                target_resource: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.DnsResourceReferenceRequest(_Model):
        properties: Optional[DnsResourceReferenceRequestProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DnsResourceReferenceRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dns.models.DnsResourceReferenceRequestProperties(_Model):
        target_resources: Optional[list[SubResource]]

        @overload
        def __init__(
                self, 
                *, 
                target_resources: Optional[list[SubResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.DnsResourceReferenceResult(_Model):
        properties: Optional[DnsResourceReferenceResultProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DnsResourceReferenceResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dns.models.DnsResourceReferenceResultProperties(_Model):
        dns_resource_references: Optional[list[DnsResourceReference]]

        @overload
        def __init__(
                self, 
                *, 
                dns_resource_references: Optional[list[DnsResourceReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.DnssecConfig(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[DnssecProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dns.models.DnssecProperties(_Model):
        provisioning_state: Optional[str]
        signing_keys: Optional[list[SigningKey]]


    class azure.mgmt.dns.models.DsRecord(_Model):
        algorithm: Optional[int]
        digest: Optional[Digest]
        key_tag: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                algorithm: Optional[int] = ..., 
                digest: Optional[Digest] = ..., 
                key_tag: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.MxRecord(_Model):
        exchange: Optional[str]
        preference: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                exchange: Optional[str] = ..., 
                preference: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.NaptrRecord(_Model):
        flags: Optional[str]
        order: Optional[int]
        preference: Optional[int]
        regexp: Optional[str]
        replacement: Optional[str]
        services: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                flags: Optional[str] = ..., 
                order: Optional[int] = ..., 
                preference: Optional[int] = ..., 
                regexp: Optional[str] = ..., 
                replacement: Optional[str] = ..., 
                services: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.NsRecord(_Model):
        nsdname: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                nsdname: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.dns.models.PtrRecord(_Model):
        ptrdname: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ptrdname: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.RecordSet(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[RecordSetProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[RecordSetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dns.models.RecordSetProperties(_Model):
        a_records: Optional[list[ARecord]]
        aaaa_records: Optional[list[AaaaRecord]]
        caa_records: Optional[list[CaaRecord]]
        cname_record: Optional[CnameRecord]
        ds_records: Optional[list[DsRecord]]
        fqdn: Optional[str]
        metadata: Optional[dict[str, str]]
        mx_records: Optional[list[MxRecord]]
        naptr_records: Optional[list[NaptrRecord]]
        ns_records: Optional[list[NsRecord]]
        provisioning_state: Optional[str]
        ptr_records: Optional[list[PtrRecord]]
        soa_record: Optional[SoaRecord]
        srv_records: Optional[list[SrvRecord]]
        target_resource: Optional[SubResource]
        tlsa_records: Optional[list[TlsaRecord]]
        traffic_management_profile: Optional[SubResource]
        ttl: Optional[int]
        txt_records: Optional[list[TxtRecord]]

        @overload
        def __init__(
                self, 
                *, 
                a_records: Optional[list[ARecord]] = ..., 
                aaaa_records: Optional[list[AaaaRecord]] = ..., 
                caa_records: Optional[list[CaaRecord]] = ..., 
                cname_record: Optional[CnameRecord] = ..., 
                ds_records: Optional[list[DsRecord]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                mx_records: Optional[list[MxRecord]] = ..., 
                naptr_records: Optional[list[NaptrRecord]] = ..., 
                ns_records: Optional[list[NsRecord]] = ..., 
                ptr_records: Optional[list[PtrRecord]] = ..., 
                soa_record: Optional[SoaRecord] = ..., 
                srv_records: Optional[list[SrvRecord]] = ..., 
                target_resource: Optional[SubResource] = ..., 
                tlsa_records: Optional[list[TlsaRecord]] = ..., 
                traffic_management_profile: Optional[SubResource] = ..., 
                ttl: Optional[int] = ..., 
                txt_records: Optional[list[TxtRecord]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.RecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A = "A"
        AAAA = "AAAA"
        CAA = "CAA"
        CNAME = "CNAME"
        DS = "DS"
        MX = "MX"
        NAPTR = "NAPTR"
        NS = "NS"
        PTR = "PTR"
        SOA = "SOA"
        SRV = "SRV"
        TLSA = "TLSA"
        TXT = "TXT"


    class azure.mgmt.dns.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.dns.models.SigningKey(_Model):
        delegation_signer_info: Optional[list[DelegationSignerInfo]]
        flags: Optional[int]
        key_tag: Optional[int]
        protocol: Optional[int]
        public_key: Optional[str]
        security_algorithm_type: Optional[int]


    class azure.mgmt.dns.models.SoaRecord(_Model):
        email: Optional[str]
        expire_time: Optional[int]
        host: Optional[str]
        minimum_ttl: Optional[int]
        refresh_time: Optional[int]
        retry_time: Optional[int]
        serial_number: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                expire_time: Optional[int] = ..., 
                host: Optional[str] = ..., 
                minimum_ttl: Optional[int] = ..., 
                refresh_time: Optional[int] = ..., 
                retry_time: Optional[int] = ..., 
                serial_number: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.SrvRecord(_Model):
        port: Optional[int]
        priority: Optional[int]
        target: Optional[str]
        weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                port: Optional[int] = ..., 
                priority: Optional[int] = ..., 
                target: Optional[str] = ..., 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.SubResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.SystemData(_Model):
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


    class azure.mgmt.dns.models.TlsaRecord(_Model):
        cert_association_data: Optional[str]
        matching_type: Optional[int]
        selector: Optional[int]
        usage: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cert_association_data: Optional[str] = ..., 
                matching_type: Optional[int] = ..., 
                selector: Optional[int] = ..., 
                usage: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.TxtRecord(_Model):
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.Zone(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[ZoneProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str, 
                properties: Optional[ZoneProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.dns.models.ZoneProperties(_Model):
        max_number_of_record_sets: Optional[int]
        max_number_of_records_per_record_set: Optional[int]
        name_servers: Optional[list[str]]
        number_of_record_sets: Optional[int]
        registration_virtual_networks: Optional[list[SubResource]]
        resolution_virtual_networks: Optional[list[SubResource]]
        signing_keys: Optional[list[SigningKey]]
        zone_type: Optional[Union[str, ZoneType]]

        @overload
        def __init__(
                self, 
                *, 
                registration_virtual_networks: Optional[list[SubResource]] = ..., 
                resolution_virtual_networks: Optional[list[SubResource]] = ..., 
                zone_type: Optional[Union[str, ZoneType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dns.models.ZoneType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.dns.models.ZoneUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.dns.operations.DnssecConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[DnssecConfig]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                **kwargs: Any
            ) -> DnssecConfig: ...

        @distributed_trace
        def list_by_dns_zone(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DnssecConfig]: ...


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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RecordSet: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                parameters: RecordSet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RecordSet: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                record_set_name_suffix: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RecordSet]: ...

        @distributed_trace
        def list_by_dns_zone(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                *, 
                recordsetnamesuffix: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RecordSet]: ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                record_type: Union[str, RecordType], 
                *, 
                recordsetnamesuffix: Optional[str] = ..., 
                top: Optional[int] = ..., 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RecordSet: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                relative_record_set_name: str, 
                record_type: Union[str, RecordType], 
                parameters: RecordSet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: Zone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: Zone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Zone]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Zone]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: ZoneUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: ZoneUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Zone: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                zone_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Zone: ...


namespace azure.mgmt.dns.types

    class azure.mgmt.dns.types.ARecord(TypedDict, total=False):
        key "ipv4Address": str
        ipv4_address: str


    class azure.mgmt.dns.types.AaaaRecord(TypedDict, total=False):
        key "ipv6Address": str
        ipv6_address: str


    class azure.mgmt.dns.types.CaaRecord(TypedDict, total=False):
        key "flags": int
        key "tag": str
        key "value": str
        flags: int
        tag: str
        value: str


    class azure.mgmt.dns.types.CnameRecord(TypedDict, total=False):
        key "cname": str
        cname: str


    class azure.mgmt.dns.types.DelegationSignerInfo(TypedDict, total=False):
        key "digestAlgorithmType": int
        key "digestValue": str
        key "record": str
        digest_algorithm_type: int
        digest_value: str
        record: str


    class azure.mgmt.dns.types.Digest(TypedDict, total=False):
        key "algorithmType": int
        key "value": str
        algorithm_type: int
        value: str


    class azure.mgmt.dns.types.DnsResourceReferenceRequest(TypedDict, total=False):
        key "properties": ForwardRef('DnsResourceReferenceRequestProperties', module='types')
        properties: DnsResourceReferenceRequestProperties


    class azure.mgmt.dns.types.DnsResourceReferenceRequestProperties(TypedDict, total=False):
        targetResources: list[SubResource]
        target_resources: list[SubResource]


    class azure.mgmt.dns.types.DsRecord(TypedDict, total=False):
        key "algorithm": int
        key "digest": ForwardRef('Digest', module='types')
        key "keyTag": int
        algorithm: int
        digest: Digest
        key_tag: int


    class azure.mgmt.dns.types.MxRecord(TypedDict, total=False):
        key "exchange": str
        key "preference": int
        exchange: str
        preference: int


    class azure.mgmt.dns.types.NaptrRecord(TypedDict, total=False):
        key "flags": str
        key "order": int
        key "preference": int
        key "regexp": str
        key "replacement": str
        key "services": str
        flags: str
        order: int
        preference: int
        regexp: str
        replacement: str
        services: str


    class azure.mgmt.dns.types.NsRecord(TypedDict, total=False):
        key "nsdname": str
        nsdname: str


    class azure.mgmt.dns.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.dns.types.PtrRecord(TypedDict, total=False):
        key "ptrdname": str
        ptrdname: str


    class azure.mgmt.dns.types.RecordSet(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('RecordSetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: RecordSetProperties
        system_data: SystemData
        type: str


    class azure.mgmt.dns.types.RecordSetProperties(TypedDict, total=False):
        key "CNAMERecord": ForwardRef('CnameRecord', module='types')
        key "SOARecord": ForwardRef('SoaRecord', module='types')
        key "TTL": int
        key "fqdn": str
        key "provisioningState": str
        key "targetResource": ForwardRef('SubResource', module='types')
        key "trafficManagementProfile": ForwardRef('SubResource', module='types')
        AAAARecords: list[AaaaRecord]
        ARecords: list[ARecord]
        DSRecords: list[DsRecord]
        MXRecords: list[MxRecord]
        NAPTRRecords: list[NaptrRecord]
        NSRecords: list[NsRecord]
        PTRRecords: list[PtrRecord]
        SRVRecords: list[SrvRecord]
        TLSARecords: list[TlsaRecord]
        TXTRecords: list[TxtRecord]
        a_records: list[ARecord]
        aaaa_records: list[AaaaRecord]
        caaRecords: list[CaaRecord]
        caa_records: list[CaaRecord]
        cname_record: CnameRecord
        ds_records: list[DsRecord]
        fqdn: str
        metadata: dict[str, str]
        mx_records: list[MxRecord]
        naptr_records: list[NaptrRecord]
        ns_records: list[NsRecord]
        provisioning_state: str
        ptr_records: list[PtrRecord]
        soa_record: SoaRecord
        srv_records: list[SrvRecord]
        target_resource: SubResource
        tlsa_records: list[TlsaRecord]
        traffic_management_profile: SubResource
        ttl: int
        txt_records: list[TxtRecord]


    class azure.mgmt.dns.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.dns.types.SigningKey(TypedDict, total=False):
        key "flags": int
        key "keyTag": int
        key "protocol": int
        key "publicKey": str
        key "securityAlgorithmType": int
        delegationSignerInfo: list[DelegationSignerInfo]
        delegation_signer_info: list[DelegationSignerInfo]
        flags: int
        key_tag: int
        protocol: int
        public_key: str
        security_algorithm_type: int


    class azure.mgmt.dns.types.SoaRecord(TypedDict, total=False):
        key "email": str
        key "expireTime": int
        key "host": str
        key "minimumTTL": int
        key "refreshTime": int
        key "retryTime": int
        key "serialNumber": int
        email: str
        expire_time: int
        host: str
        minimum_ttl: int
        refresh_time: int
        retry_time: int
        serial_number: int


    class azure.mgmt.dns.types.SrvRecord(TypedDict, total=False):
        key "port": int
        key "priority": int
        key "target": str
        key "weight": int
        port: int
        priority: int
        target: str
        weight: int


    class azure.mgmt.dns.types.SubResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.dns.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.dns.types.TlsaRecord(TypedDict, total=False):
        key "certAssociationData": str
        key "matchingType": int
        key "selector": int
        key "usage": int
        cert_association_data: str
        matching_type: int
        selector: int
        usage: int


    class azure.mgmt.dns.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.dns.types.TxtRecord(TypedDict, total=False):
        value: list[str]


    class azure.mgmt.dns.types.Zone(TrackedResource):
        key "etag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ZoneProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: ZoneProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.dns.types.ZoneProperties(TypedDict, total=False):
        key "maxNumberOfRecordSets": int
        key "maxNumberOfRecordsPerRecordSet": int
        key "numberOfRecordSets": int
        key "zoneType": Union[str, ZoneType]
        max_number_of_record_sets: int
        max_number_of_records_per_record_set: int
        nameServers: list[str]
        name_servers: list[str]
        number_of_record_sets: int
        registrationVirtualNetworks: list[SubResource]
        registration_virtual_networks: list[SubResource]
        resolutionVirtualNetworks: list[SubResource]
        resolution_virtual_networks: list[SubResource]
        signingKeys: list[SigningKey]
        signing_keys: list[SigningKey]
        zone_type: Union[str, ZoneType]


    class azure.mgmt.dns.types.ZoneUpdate(TypedDict, total=False):
        tags: dict[str, str]


```