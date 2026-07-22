```py
namespace azure.mgmt.privatedns

    class azure.mgmt.privatedns.PrivateDnsManagementClient: implements ContextManager 
        private_zones: PrivateZonesOperations
        record_sets: RecordSetsOperations
        virtual_network_links: VirtualNetworkLinksOperations

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


namespace azure.mgmt.privatedns.aio

    class azure.mgmt.privatedns.aio.PrivateDnsManagementClient: implements AsyncContextManager 
        private_zones: PrivateZonesOperations
        record_sets: RecordSetsOperations
        virtual_network_links: VirtualNetworkLinksOperations

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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateZone]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateZone]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateZone]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateZone]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateZone]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateZone]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateZone]: ...


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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                recordsetnamesuffix: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RecordSet]: ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualNetworkLink]: ...


namespace azure.mgmt.privatedns.models

    class azure.mgmt.privatedns.models.ARecord(_Model):
        ipv4_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatedns.models.AaaaRecord(_Model):
        ipv6_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ipv6_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatedns.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatedns.models.CloudErrorBody(_Model):
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


    class azure.mgmt.privatedns.models.CnameRecord(_Model):
        cname: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cname: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatedns.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.privatedns.models.MxRecord(_Model):
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


    class azure.mgmt.privatedns.models.PrivateZone(ProxyResource):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[PrivateZoneProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[PrivateZoneProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.privatedns.models.PrivateZoneProperties(_Model):
        internal_id: Optional[str]
        max_number_of_record_sets: Optional[int]
        max_number_of_virtual_network_links: Optional[int]
        max_number_of_virtual_network_links_with_registration: Optional[int]
        number_of_record_sets: Optional[int]
        number_of_virtual_network_links: Optional[int]
        number_of_virtual_network_links_with_registration: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]


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
        system_data: SystemData
        type: str


    class azure.mgmt.privatedns.models.PtrRecord(_Model):
        ptrdname: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ptrdname: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatedns.models.RecordSet(ProxyResource):
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


    class azure.mgmt.privatedns.models.RecordSetProperties(_Model):
        a_records: Optional[list[ARecord]]
        aaaa_records: Optional[list[AaaaRecord]]
        cname_record: Optional[CnameRecord]
        fqdn: Optional[str]
        is_auto_registered: Optional[bool]
        metadata: Optional[dict[str, str]]
        mx_records: Optional[list[MxRecord]]
        ptr_records: Optional[list[PtrRecord]]
        soa_record: Optional[SoaRecord]
        srv_records: Optional[list[SrvRecord]]
        ttl: Optional[int]
        txt_records: Optional[list[TxtRecord]]

        @overload
        def __init__(
                self, 
                *, 
                a_records: Optional[list[ARecord]] = ..., 
                aaaa_records: Optional[list[AaaaRecord]] = ..., 
                cname_record: Optional[CnameRecord] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                mx_records: Optional[list[MxRecord]] = ..., 
                ptr_records: Optional[list[PtrRecord]] = ..., 
                soa_record: Optional[SoaRecord] = ..., 
                srv_records: Optional[list[SrvRecord]] = ..., 
                ttl: Optional[int] = ..., 
                txt_records: Optional[list[TxtRecord]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.privatedns.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.privatedns.models.SoaRecord(_Model):
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


    class azure.mgmt.privatedns.models.SrvRecord(_Model):
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


    class azure.mgmt.privatedns.models.SubResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatedns.models.SystemData(_Model):
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


    class azure.mgmt.privatedns.models.TxtRecord(_Model):
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatedns.models.VirtualNetworkLink(ProxyResource):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[VirtualNetworkLinkProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[VirtualNetworkLinkProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.privatedns.models.VirtualNetworkLinkProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        registration_enabled: Optional[bool]
        resolution_policy: Optional[Union[str, ResolutionPolicy]]
        virtual_network: Optional[SubResource]
        virtual_network_link_state: Optional[Union[str, VirtualNetworkLinkState]]

        @overload
        def __init__(
                self, 
                *, 
                registration_enabled: Optional[bool] = ..., 
                resolution_policy: Optional[Union[str, ResolutionPolicy]] = ..., 
                virtual_network: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.privatedns.models.VirtualNetworkLinkState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        IN_PROGRESS = "InProgress"


namespace azure.mgmt.privatedns.operations

    class azure.mgmt.privatedns.operations.PrivateZonesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PrivateZone]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PrivateZone]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PrivateZone]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PrivateZone]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: PrivateZone, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PrivateZone]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrivateZone]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrivateZone]: ...


    class azure.mgmt.privatedns.operations.RecordSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                recordsetnamesuffix: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RecordSet]: ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
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
                private_zone_name: str, 
                record_type: Union[str, RecordType], 
                relative_record_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> RecordSet: ...


    class azure.mgmt.privatedns.operations.VirtualNetworkLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: VirtualNetworkLink, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_zone_name: str, 
                virtual_network_link_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualNetworkLink]: ...


namespace azure.mgmt.privatedns.types

    class azure.mgmt.privatedns.types.ARecord(TypedDict, total=False):
        key "ipv4Address": str
        ipv4_address: str


    class azure.mgmt.privatedns.types.AaaaRecord(TypedDict, total=False):
        key "ipv6Address": str
        ipv6_address: str


    class azure.mgmt.privatedns.types.CloudError(TypedDict, total=False):
        key "error": ForwardRef('CloudErrorBody', module='types')
        error: CloudErrorBody


    class azure.mgmt.privatedns.types.CloudErrorBody(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str


    class azure.mgmt.privatedns.types.CnameRecord(TypedDict, total=False):
        key "cname": str
        cname: str


    class azure.mgmt.privatedns.types.MxRecord(TypedDict, total=False):
        key "exchange": str
        key "preference": int
        exchange: str
        preference: int


    class azure.mgmt.privatedns.types.PrivateZone(ProxyResource):
        key "etag": str
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('PrivateZoneProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: PrivateZoneProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.privatedns.types.PrivateZoneProperties(TypedDict, total=False):
        key "internalId": str
        key "maxNumberOfRecordSets": int
        key "maxNumberOfVirtualNetworkLinks": int
        key "maxNumberOfVirtualNetworkLinksWithRegistration": int
        key "numberOfRecordSets": int
        key "numberOfVirtualNetworkLinks": int
        key "numberOfVirtualNetworkLinksWithRegistration": int
        key "provisioningState": Union[str, ProvisioningState]
        internal_id: str
        max_number_of_record_sets: int
        max_number_of_virtual_network_links: int
        max_number_of_virtual_network_links_with_registration: int
        number_of_record_sets: int
        number_of_virtual_network_links: int
        number_of_virtual_network_links_with_registration: int
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.privatedns.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.privatedns.types.PtrRecord(TypedDict, total=False):
        key "ptrdname": str
        ptrdname: str


    class azure.mgmt.privatedns.types.RecordSet(ProxyResource):
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


    class azure.mgmt.privatedns.types.RecordSetProperties(TypedDict, total=False):
        key "cnameRecord": ForwardRef('CnameRecord', module='types')
        key "fqdn": str
        key "isAutoRegistered": bool
        key "soaRecord": ForwardRef('SoaRecord', module='types')
        key "ttl": int
        aRecords: list[ARecord]
        a_records: list[ARecord]
        aaaaRecords: list[AaaaRecord]
        aaaa_records: list[AaaaRecord]
        cname_record: CnameRecord
        fqdn: str
        is_auto_registered: bool
        metadata: dict[str, str]
        mxRecords: list[MxRecord]
        mx_records: list[MxRecord]
        ptrRecords: list[PtrRecord]
        ptr_records: list[PtrRecord]
        soa_record: SoaRecord
        srvRecords: list[SrvRecord]
        srv_records: list[SrvRecord]
        ttl: int
        txtRecords: list[TxtRecord]
        txt_records: list[TxtRecord]


    class azure.mgmt.privatedns.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.privatedns.types.SoaRecord(TypedDict, total=False):
        key "email": str
        key "expireTime": int
        key "host": str
        key "minimumTtl": int
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


    class azure.mgmt.privatedns.types.SrvRecord(TypedDict, total=False):
        key "port": int
        key "priority": int
        key "target": str
        key "weight": int
        port: int
        priority: int
        target: str
        weight: int


    class azure.mgmt.privatedns.types.SubResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.privatedns.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.privatedns.types.TxtRecord(TypedDict, total=False):
        value: list[str]


    class azure.mgmt.privatedns.types.VirtualNetworkLink(ProxyResource):
        key "etag": str
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('VirtualNetworkLinkProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: VirtualNetworkLinkProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.privatedns.types.VirtualNetworkLinkProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "registrationEnabled": bool
        key "resolutionPolicy": Union[str, ResolutionPolicy]
        key "virtualNetwork": ForwardRef('SubResource', module='types')
        key "virtualNetworkLinkState": Union[str, VirtualNetworkLinkState]
        provisioning_state: Union[str, ProvisioningState]
        registration_enabled: bool
        resolution_policy: Union[str, ResolutionPolicy]
        virtual_network: SubResource
        virtual_network_link_state: Union[str, VirtualNetworkLinkState]


```