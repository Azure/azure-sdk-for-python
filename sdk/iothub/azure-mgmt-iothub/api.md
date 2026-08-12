```py
namespace azure.mgmt.iothub

    class azure.mgmt.iothub.IotHubClient: implements ContextManager 
        certificates: CertificatesOperations
        iot_hub: IotHubOperations
        iot_hub_resource: IotHubResourceOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        resource_provider_common: ResourceProviderCommonOperations

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


namespace azure.mgmt.iothub.aio

    class azure.mgmt.iothub.aio.IotHubClient: implements AsyncContextManager 
        certificates: CertificatesOperations
        iot_hub: IotHubOperations
        iot_hub_resource: IotHubResourceOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        resource_provider_common: ResourceProviderCommonOperations

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


namespace azure.mgmt.iothub.aio.operations

    class azure.mgmt.iothub.aio.operations.CertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_description: CertificateDescription, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_description: CertificateDescription, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_description: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def generate_verification_code(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateWithNonceDescription: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @distributed_trace_async
        async def list_by_iot_hub(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> CertificateListDescription: ...

        @overload
        async def verify(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_verification_body: CertificateVerificationDescription, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @overload
        async def verify(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_verification_body: CertificateVerificationDescription, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @overload
        async def verify(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_verification_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateDescription: ...


    class azure.mgmt.iothub.aio.operations.IotHubOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_manual_failover(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                failover_input: FailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_manual_failover(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                failover_input: FailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_manual_failover(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                failover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.iothub.aio.operations.IotHubResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_description: IotHubDescription, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[IotHubDescription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_description: IotHubDescription, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[IotHubDescription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_description: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[IotHubDescription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[IotHubDescription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IotHubDescription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IotHubDescription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IotHubDescription]: ...

        @overload
        async def check_name_availability(
                self, 
                operation_inputs: OperationInputs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IotHubNameAvailabilityInfo: ...

        @overload
        async def check_name_availability(
                self, 
                operation_inputs: OperationInputs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IotHubNameAvailabilityInfo: ...

        @overload
        async def check_name_availability(
                self, 
                operation_inputs: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IotHubNameAvailabilityInfo: ...

        @overload
        async def create_event_hub_consumer_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                name: str, 
                consumer_group_body: EventHubConsumerGroupBodyDescription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventHubConsumerGroupInfo: ...

        @overload
        async def create_event_hub_consumer_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                name: str, 
                consumer_group_body: EventHubConsumerGroupBodyDescription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventHubConsumerGroupInfo: ...

        @overload
        async def create_event_hub_consumer_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                name: str, 
                consumer_group_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventHubConsumerGroupInfo: ...

        @distributed_trace_async
        async def delete_event_hub_consumer_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def export_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_devices_parameters: ExportDevicesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        async def export_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_devices_parameters: ExportDevicesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        async def export_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_devices_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> IotHubDescription: ...

        @distributed_trace
        def get_endpoint_health(
                self, 
                resource_group_name: str, 
                iot_hub_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EndpointHealthData]: ...

        @distributed_trace_async
        async def get_event_hub_consumer_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                name: str, 
                **kwargs: Any
            ) -> EventHubConsumerGroupInfo: ...

        @distributed_trace_async
        async def get_job(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> JobResponse: ...

        @distributed_trace_async
        async def get_keys_for_key_name(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                key_name: str, 
                **kwargs: Any
            ) -> SharedAccessSignatureAuthorizationRule: ...

        @distributed_trace
        def get_quota_metrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IotHubQuotaMetricInfo]: ...

        @distributed_trace_async
        async def get_stats(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> RegistryStatistics: ...

        @distributed_trace
        def get_valid_skus(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IotHubSkuDescription]: ...

        @overload
        async def import_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                import_devices_parameters: ImportDevicesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        async def import_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                import_devices_parameters: ImportDevicesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        async def import_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                import_devices_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IotHubDescription]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[IotHubDescription]: ...

        @distributed_trace
        def list_event_hub_consumer_groups(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventHubConsumerGroupInfo]: ...

        @distributed_trace
        def list_jobs(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JobResponse]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedAccessSignatureAuthorizationRule]: ...

        @overload
        async def test_all_routes(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: TestAllRoutesInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestAllRoutesResult: ...

        @overload
        async def test_all_routes(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: TestAllRoutesInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestAllRoutesResult: ...

        @overload
        async def test_all_routes(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestAllRoutesResult: ...

        @overload
        async def test_route(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: TestRouteInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestRouteResult: ...

        @overload
        async def test_route(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: TestRouteInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestRouteResult: ...

        @overload
        async def test_route(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestRouteResult: ...


    class azure.mgmt.iothub.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.iothub.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> List[PrivateEndpointConnection]: ...


    class azure.mgmt.iothub.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                group_id: str, 
                **kwargs: Any
            ) -> GroupIdInformation: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResources: ...


    class azure.mgmt.iothub.aio.operations.ResourceProviderCommonOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_subscription_quota(self, **kwargs: Any) -> UserSubscriptionQuotaListResult: ...


namespace azure.mgmt.iothub.models

    class azure.mgmt.iothub.models.AccessRights(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVICE_CONNECT = "DeviceConnect"
        REGISTRY_READ = "RegistryRead"
        REGISTRY_READ_DEVICE_CONNECT = "RegistryRead, DeviceConnect"
        REGISTRY_READ_REGISTRY_WRITE = "RegistryRead, RegistryWrite"
        REGISTRY_READ_REGISTRY_WRITE_DEVICE_CONNECT = "RegistryRead, RegistryWrite, DeviceConnect"
        REGISTRY_READ_REGISTRY_WRITE_SERVICE_CONNECT = "RegistryRead, RegistryWrite, ServiceConnect"
        REGISTRY_READ_REGISTRY_WRITE_SERVICE_CONNECT_DEVICE_CONNECT = "RegistryRead, RegistryWrite, ServiceConnect, DeviceConnect"
        REGISTRY_READ_SERVICE_CONNECT = "RegistryRead, ServiceConnect"
        REGISTRY_READ_SERVICE_CONNECT_DEVICE_CONNECT = "RegistryRead, ServiceConnect, DeviceConnect"
        REGISTRY_WRITE = "RegistryWrite"
        REGISTRY_WRITE_DEVICE_CONNECT = "RegistryWrite, DeviceConnect"
        REGISTRY_WRITE_SERVICE_CONNECT = "RegistryWrite, ServiceConnect"
        REGISTRY_WRITE_SERVICE_CONNECT_DEVICE_CONNECT = "RegistryWrite, ServiceConnect, DeviceConnect"
        SERVICE_CONNECT = "ServiceConnect"
        SERVICE_CONNECT_DEVICE_CONNECT = "ServiceConnect, DeviceConnect"


    class azure.mgmt.iothub.models.ArmIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, ArmUserIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, ArmUserIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.ArmUserIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.iothub.models.AuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IDENTITY_BASED = "identityBased"
        KEY_BASED = "keyBased"


    class azure.mgmt.iothub.models.Capabilities(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVICE_MANAGEMENT = "DeviceManagement"
        NONE = "None"


    class azure.mgmt.iothub.models.CertificateDescription(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[CertificateProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CertificateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.CertificateListDescription(_Model):
        value: Optional[list[CertificateDescription]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[CertificateDescription]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.CertificateProperties(_Model):
        certificate: Optional[str]
        created: Optional[datetime]
        expiry: Optional[datetime]
        is_verified: Optional[bool]
        policy_resource_id: Optional[str]
        subject: Optional[str]
        thumbprint: Optional[str]
        updated: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                certificate: Optional[str] = ..., 
                is_verified: Optional[bool] = ..., 
                policy_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.CertificatePropertiesWithNonce(_Model):
        certificate: Optional[str]
        created: Optional[datetime]
        expiry: Optional[datetime]
        is_verified: Optional[bool]
        policy_resource_id: Optional[str]
        subject: Optional[str]
        thumbprint: Optional[str]
        updated: Optional[datetime]
        verification_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                policy_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.CertificateVerificationDescription(_Model):
        certificate: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.CertificateWithNonceDescription(_Model):
        etag: Optional[str]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[CertificatePropertiesWithNonce]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CertificatePropertiesWithNonce] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.CloudToDeviceProperties(_Model):
        default_ttl_as_iso8601: Optional[timedelta]
        feedback: Optional[FeedbackProperties]
        max_delivery_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                default_ttl_as_iso8601: Optional[timedelta] = ..., 
                feedback: Optional[FeedbackProperties] = ..., 
                max_delivery_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.iothub.models.DefaultAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.iothub.models.DeviceRegistry(_Model):
        identity_resource_id: Optional[str]
        namespace_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_resource_id: Optional[str] = ..., 
                namespace_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.EncryptionPropertiesDescription(_Model):
        key_source: Optional[str]
        key_vault_properties: Optional[list[KeyVaultKeyProperties]]

        @overload
        def __init__(
                self, 
                *, 
                key_source: Optional[str] = ..., 
                key_vault_properties: Optional[list[KeyVaultKeyProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.EndpointHealthData(_Model):
        endpoint_id: Optional[str]
        health_status: Optional[Union[str, EndpointHealthStatus]]
        last_known_error: Optional[str]
        last_known_error_time: Optional[datetime]
        last_send_attempt_time: Optional[datetime]
        last_successful_send_attempt_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_id: Optional[str] = ..., 
                health_status: Optional[Union[str, EndpointHealthStatus]] = ..., 
                last_known_error: Optional[str] = ..., 
                last_known_error_time: Optional[datetime] = ..., 
                last_send_attempt_time: Optional[datetime] = ..., 
                last_successful_send_attempt_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.EndpointHealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEAD = "dead"
        DEGRADED = "degraded"
        HEALTHY = "healthy"
        UNHEALTHY = "unhealthy"
        UNKNOWN = "unknown"


    class azure.mgmt.iothub.models.EnrichmentProperties(_Model):
        endpoint_names: list[str]
        key: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                endpoint_names: list[str], 
                key: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.ErrorDetails(_Model):
        code: Optional[str]
        details: Optional[str]
        http_status_code: Optional[str]
        message: Optional[str]


    class azure.mgmt.iothub.models.EventHubConsumerGroupBodyDescription(_Model):
        properties: EventHubConsumerGroupName

        @overload
        def __init__(
                self, 
                *, 
                properties: EventHubConsumerGroupName
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.EventHubConsumerGroupInfo(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[dict[str, Any]]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.EventHubConsumerGroupName(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.EventHubProperties(_Model):
        endpoint: Optional[str]
        partition_count: Optional[int]
        partition_ids: Optional[list[str]]
        path: Optional[str]
        retention_time_in_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                partition_count: Optional[int] = ..., 
                retention_time_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.EventStreamAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IDENTITY_BASED = "identityBased"


    class azure.mgmt.iothub.models.ExportDevicesRequest(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        configurations_blob_name: Optional[str]
        exclude_keys: bool
        export_blob_container_uri: str
        export_blob_name: Optional[str]
        identity: Optional[ManagedIdentity]
        include_configurations: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                configurations_blob_name: Optional[str] = ..., 
                exclude_keys: bool, 
                export_blob_container_uri: str, 
                export_blob_name: Optional[str] = ..., 
                identity: Optional[ManagedIdentity] = ..., 
                include_configurations: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.FailoverInput(_Model):
        failover_region: str

        @overload
        def __init__(
                self, 
                *, 
                failover_region: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.FallbackRouteProperties(_Model):
        condition: Optional[str]
        endpoint_names: list[str]
        is_enabled: bool
        name: Optional[str]
        source: Union[str, RoutingSource]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ..., 
                endpoint_names: list[str], 
                is_enabled: bool, 
                name: Optional[str] = ..., 
                source: Union[str, RoutingSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.FeedbackProperties(_Model):
        lock_duration_as_iso8601: Optional[timedelta]
        max_delivery_count: Optional[int]
        ttl_as_iso8601: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                lock_duration_as_iso8601: Optional[timedelta] = ..., 
                max_delivery_count: Optional[int] = ..., 
                ttl_as_iso8601: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.GatewayVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V1 = "V1"
        V2 = "V2"


    class azure.mgmt.iothub.models.GroupIdInformation(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: GroupIdInformationProperties
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: GroupIdInformationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.GroupIdInformationProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                required_members: Optional[list[str]] = ..., 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.ImportDevicesRequest(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        configurations_blob_name: Optional[str]
        identity: Optional[ManagedIdentity]
        include_configurations: Optional[bool]
        input_blob_container_uri: str
        input_blob_name: Optional[str]
        output_blob_container_uri: str
        output_blob_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                configurations_blob_name: Optional[str] = ..., 
                identity: Optional[ManagedIdentity] = ..., 
                include_configurations: Optional[bool] = ..., 
                input_blob_container_uri: str, 
                input_blob_name: Optional[str] = ..., 
                output_blob_container_uri: str, 
                output_blob_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.IotHubCapacity(_Model):
        default: Optional[int]
        maximum: Optional[int]
        minimum: Optional[int]
        scale_type: Optional[Union[str, IotHubScaleType]]


    class azure.mgmt.iothub.models.IotHubDescription(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ArmIdentity]
        location: str
        name: str
        properties: Optional[IotHubProperties]
        sku: IotHubSkuInfo
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                identity: Optional[ArmIdentity] = ..., 
                location: str, 
                properties: Optional[IotHubProperties] = ..., 
                sku: IotHubSkuInfo, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.IotHubDetails(_Model):
        gateway_version: Optional[Union[str, GatewayVersion]]

        @overload
        def __init__(
                self, 
                *, 
                gateway_version: Optional[Union[str, GatewayVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.IotHubLocationDescription(_Model):
        location: Optional[str]
        role: Optional[Union[str, IotHubReplicaRoleType]]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                role: Optional[Union[str, IotHubReplicaRoleType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.IotHubNameAvailabilityInfo(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, IotHubNameUnavailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.IotHubNameUnavailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.iothub.models.IotHubProperties(_Model):
        allowed_fqdn_list: Optional[list[str]]
        authorization_policies: Optional[list[SharedAccessSignatureAuthorizationRule]]
        cloud_to_device: Optional[CloudToDeviceProperties]
        comments: Optional[str]
        device_host_name: Optional[str]
        device_registry: Optional[DeviceRegistry]
        device_streams: Optional[IotHubPropertiesDeviceStreams]
        disable_device_sas: Optional[bool]
        disable_local_auth: Optional[bool]
        disable_module_sas: Optional[bool]
        enable_data_residency: Optional[bool]
        enable_file_upload_notifications: Optional[bool]
        encryption: Optional[EncryptionPropertiesDescription]
        event_hub_endpoints: Optional[dict[str, EventHubProperties]]
        features: Optional[Union[str, Capabilities]]
        host_name: Optional[str]
        iot_hub_details: Optional[IotHubDetails]
        ip_filter_rules: Optional[list[IpFilterRule]]
        ip_version: Optional[Union[str, IpVersion]]
        locations: Optional[list[IotHubLocationDescription]]
        messaging_endpoints: Optional[dict[str, MessagingEndpointProperties]]
        min_tls_version: Optional[str]
        network_rule_sets: Optional[NetworkRuleSetProperties]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        restrict_outbound_network_access: Optional[bool]
        root_certificate: Optional[RootCertificateProperties]
        routing: Optional[RoutingProperties]
        service_host_name: Optional[str]
        state: Optional[str]
        storage_endpoints: Optional[dict[str, StorageEndpointProperties]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_fqdn_list: Optional[list[str]] = ..., 
                authorization_policies: Optional[list[SharedAccessSignatureAuthorizationRule]] = ..., 
                cloud_to_device: Optional[CloudToDeviceProperties] = ..., 
                comments: Optional[str] = ..., 
                device_registry: Optional[DeviceRegistry] = ..., 
                device_streams: Optional[IotHubPropertiesDeviceStreams] = ..., 
                disable_device_sas: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                disable_module_sas: Optional[bool] = ..., 
                enable_data_residency: Optional[bool] = ..., 
                enable_file_upload_notifications: Optional[bool] = ..., 
                encryption: Optional[EncryptionPropertiesDescription] = ..., 
                event_hub_endpoints: Optional[dict[str, EventHubProperties]] = ..., 
                features: Optional[Union[str, Capabilities]] = ..., 
                ip_filter_rules: Optional[list[IpFilterRule]] = ..., 
                ip_version: Optional[Union[str, IpVersion]] = ..., 
                messaging_endpoints: Optional[dict[str, MessagingEndpointProperties]] = ..., 
                min_tls_version: Optional[str] = ..., 
                network_rule_sets: Optional[NetworkRuleSetProperties] = ..., 
                private_endpoint_connections: Optional[list[PrivateEndpointConnection]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                restrict_outbound_network_access: Optional[bool] = ..., 
                root_certificate: Optional[RootCertificateProperties] = ..., 
                routing: Optional[RoutingProperties] = ..., 
                storage_endpoints: Optional[dict[str, StorageEndpointProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.IotHubPropertiesDeviceStreams(_Model):
        streaming_endpoints: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                streaming_endpoints: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.IotHubQuotaMetricInfo(_Model):
        current_value: Optional[int]
        max_value: Optional[int]
        name: Optional[str]


    class azure.mgmt.iothub.models.IotHubReplicaRoleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "primary"
        SECONDARY = "secondary"


    class azure.mgmt.iothub.models.IotHubScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.iothub.models.IotHubSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        B1 = "B1"
        B2 = "B2"
        B3 = "B3"
        F1 = "F1"
        S1 = "S1"
        S2 = "S2"
        S3 = "S3"


    class azure.mgmt.iothub.models.IotHubSkuDescription(_Model):
        capacity: IotHubCapacity
        resource_type: Optional[str]
        sku: IotHubSkuInfo

        @overload
        def __init__(
                self, 
                *, 
                capacity: IotHubCapacity, 
                sku: IotHubSkuInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.IotHubSkuInfo(_Model):
        capacity: Optional[int]
        name: Union[str, IotHubSku]
        tier: Optional[Union[str, IotHubSkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, IotHubSku]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.IotHubSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        STANDARD = "Standard"


    class azure.mgmt.iothub.models.IpFilterActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPT = "Accept"
        REJECT = "Reject"


    class azure.mgmt.iothub.models.IpFilterRule(_Model):
        action: Union[str, IpFilterActionType]
        filter_name: str
        ip_mask: str

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, IpFilterActionType], 
                filter_name: str, 
                ip_mask: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.IpVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IPV4 = "ipv4"
        IPV4_IPV6 = "ipv4ipv6"
        IPV6 = "ipv6"


    class azure.mgmt.iothub.models.JobResponse(_Model):
        end_time_utc: Optional[datetime]
        failure_reason: Optional[str]
        job_id: Optional[str]
        parent_job_id: Optional[str]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, JobStatus]]
        status_message: Optional[str]
        type: Optional[Union[str, JobType]]


    class azure.mgmt.iothub.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        COMPLETED = "completed"
        ENQUEUED = "enqueued"
        FAILED = "failed"
        RUNNING = "running"
        UNKNOWN = "unknown"


    class azure.mgmt.iothub.models.JobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP = "backup"
        EXPORT = "export"
        FACTORY_RESET_DEVICE = "factoryResetDevice"
        FIRMWARE_UPDATE = "firmwareUpdate"
        IMPORT = "import"
        READ_DEVICE_PROPERTIES = "readDeviceProperties"
        REBOOT_DEVICE = "rebootDevice"
        UNKNOWN = "unknown"
        UPDATE_DEVICE_CONFIGURATION = "updateDeviceConfiguration"
        WRITE_DEVICE_PROPERTIES = "writeDeviceProperties"


    class azure.mgmt.iothub.models.KeyVaultKeyProperties(_Model):
        identity: Optional[ManagedIdentity]
        key_identifier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedIdentity] = ..., 
                key_identifier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.ManagedIdentity(_Model):
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.MatchedRoute(_Model):
        properties: Optional[RouteProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RouteProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.MessagingEndpointProperties(_Model):
        lock_duration_as_iso8601: Optional[timedelta]
        max_delivery_count: Optional[int]
        ttl_as_iso8601: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                lock_duration_as_iso8601: Optional[timedelta] = ..., 
                max_delivery_count: Optional[int] = ..., 
                ttl_as_iso8601: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.Name(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.NetworkRuleIPAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"


    class azure.mgmt.iothub.models.NetworkRuleSetIpRule(_Model):
        action: Optional[Union[str, NetworkRuleIPAction]]
        filter_name: str
        ip_mask: str

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, NetworkRuleIPAction]] = ..., 
                filter_name: str, 
                ip_mask: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.NetworkRuleSetProperties(_Model):
        apply_to_built_in_event_hub_endpoint: bool
        default_action: Optional[Union[str, DefaultAction]]
        ip_rules: list[NetworkRuleSetIpRule]

        @overload
        def __init__(
                self, 
                *, 
                apply_to_built_in_event_hub_endpoint: bool, 
                default_action: Optional[Union[str, DefaultAction]] = ..., 
                ip_rules: list[NetworkRuleSetIpRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.iothub.models.OperationInputs(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.iothub.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: PrivateEndpointConnectionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.PrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.PrivateLinkResources(_Model):
        value: Optional[list[GroupIdInformation]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[GroupIdInformation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: str
        status: Union[str, PrivateLinkServiceConnectionStatus]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: str, 
                status: Union[str, PrivateLinkServiceConnectionStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.PrivateLinkServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.iothub.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.iothub.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.iothub.models.RegistryStatistics(_Model):
        disabled_device_count: Optional[int]
        enabled_device_count: Optional[int]
        total_device_count: Optional[int]


    class azure.mgmt.iothub.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.iothub.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.iothub.models.RootCertificateProperties(_Model):
        enable_root_certificate_v2: Optional[bool]
        last_updated_time_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                enable_root_certificate_v2: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RouteCompilationError(_Model):
        location: Optional[RouteErrorRange]
        message: Optional[str]
        severity: Optional[Union[str, RouteErrorSeverity]]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[RouteErrorRange] = ..., 
                message: Optional[str] = ..., 
                severity: Optional[Union[str, RouteErrorSeverity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RouteErrorPosition(_Model):
        column: Optional[int]
        line: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                column: Optional[int] = ..., 
                line: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RouteErrorRange(_Model):
        end: Optional[RouteErrorPosition]
        start: Optional[RouteErrorPosition]

        @overload
        def __init__(
                self, 
                *, 
                end: Optional[RouteErrorPosition] = ..., 
                start: Optional[RouteErrorPosition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RouteErrorSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "error"
        WARNING = "warning"


    class azure.mgmt.iothub.models.RouteProperties(_Model):
        condition: Optional[str]
        endpoint_names: list[str]
        is_enabled: bool
        name: str
        source: Union[str, RoutingSource]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ..., 
                endpoint_names: list[str], 
                is_enabled: bool, 
                name: str, 
                source: Union[str, RoutingSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingCosmosDBSqlApiProperties(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        container_name: str
        database_name: str
        endpoint_uri: str
        id: Optional[str]
        identity: Optional[ManagedIdentity]
        name: str
        partition_key_name: Optional[str]
        partition_key_template: Optional[str]
        primary_key: Optional[str]
        resource_group: Optional[str]
        secondary_key: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                container_name: str, 
                database_name: str, 
                endpoint_uri: str, 
                identity: Optional[ManagedIdentity] = ..., 
                name: str, 
                partition_key_name: Optional[str] = ..., 
                partition_key_template: Optional[str] = ..., 
                primary_key: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                secondary_key: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingEndpoints(_Model):
        cosmos_db_sql_containers: Optional[list[RoutingCosmosDBSqlApiProperties]]
        event_hubs: Optional[list[RoutingEventHubProperties]]
        event_streams: Optional[list[RoutingEventStreamProperties]]
        service_bus_queues: Optional[list[RoutingServiceBusQueueEndpointProperties]]
        service_bus_topics: Optional[list[RoutingServiceBusTopicEndpointProperties]]
        storage_containers: Optional[list[RoutingStorageContainerProperties]]

        @overload
        def __init__(
                self, 
                *, 
                cosmos_db_sql_containers: Optional[list[RoutingCosmosDBSqlApiProperties]] = ..., 
                event_hubs: Optional[list[RoutingEventHubProperties]] = ..., 
                event_streams: Optional[list[RoutingEventStreamProperties]] = ..., 
                service_bus_queues: Optional[list[RoutingServiceBusQueueEndpointProperties]] = ..., 
                service_bus_topics: Optional[list[RoutingServiceBusTopicEndpointProperties]] = ..., 
                storage_containers: Optional[list[RoutingStorageContainerProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingEventHubProperties(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        connection_string: Optional[str]
        endpoint_uri: Optional[str]
        entity_path: Optional[str]
        id: Optional[str]
        identity: Optional[ManagedIdentity]
        name: str
        resource_group: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                connection_string: Optional[str] = ..., 
                endpoint_uri: Optional[str] = ..., 
                entity_path: Optional[str] = ..., 
                id: Optional[str] = ..., 
                identity: Optional[ManagedIdentity] = ..., 
                name: str, 
                resource_group: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingEventStreamProperties(_Model):
        authentication_type: Optional[Union[str, EventStreamAuthenticationType]]
        endpoint_uri: str
        entity_path: str
        event_stream_id: Optional[str]
        id: Optional[str]
        identity: Optional[ManagedIdentity]
        name: str
        source_id: Optional[str]
        workspace_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, EventStreamAuthenticationType]] = ..., 
                endpoint_uri: str, 
                entity_path: str, 
                event_stream_id: Optional[str] = ..., 
                identity: Optional[ManagedIdentity] = ..., 
                name: str, 
                source_id: Optional[str] = ..., 
                workspace_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingMessage(_Model):
        app_properties: Optional[dict[str, str]]
        body: Optional[str]
        system_properties: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                app_properties: Optional[dict[str, str]] = ..., 
                body: Optional[str] = ..., 
                system_properties: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingProperties(_Model):
        endpoints: Optional[RoutingEndpoints]
        enrichments: Optional[list[EnrichmentProperties]]
        fallback_route: Optional[FallbackRouteProperties]
        routes: Optional[list[RouteProperties]]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: Optional[RoutingEndpoints] = ..., 
                enrichments: Optional[list[EnrichmentProperties]] = ..., 
                fallback_route: Optional[FallbackRouteProperties] = ..., 
                routes: Optional[list[RouteProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingServiceBusQueueEndpointProperties(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        connection_string: Optional[str]
        endpoint_uri: Optional[str]
        entity_path: Optional[str]
        id: Optional[str]
        identity: Optional[ManagedIdentity]
        name: str
        resource_group: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                connection_string: Optional[str] = ..., 
                endpoint_uri: Optional[str] = ..., 
                entity_path: Optional[str] = ..., 
                id: Optional[str] = ..., 
                identity: Optional[ManagedIdentity] = ..., 
                name: str, 
                resource_group: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingServiceBusTopicEndpointProperties(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        connection_string: Optional[str]
        endpoint_uri: Optional[str]
        entity_path: Optional[str]
        id: Optional[str]
        identity: Optional[ManagedIdentity]
        name: str
        resource_group: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                connection_string: Optional[str] = ..., 
                endpoint_uri: Optional[str] = ..., 
                entity_path: Optional[str] = ..., 
                id: Optional[str] = ..., 
                identity: Optional[ManagedIdentity] = ..., 
                name: str, 
                resource_group: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVICE_CONNECTION_STATE_EVENTS = "DeviceConnectionStateEvents"
        DEVICE_JOB_LIFECYCLE_EVENTS = "DeviceJobLifecycleEvents"
        DEVICE_LIFECYCLE_EVENTS = "DeviceLifecycleEvents"
        DEVICE_MESSAGES = "DeviceMessages"
        DIGITAL_TWIN_CHANGE_EVENTS = "DigitalTwinChangeEvents"
        INVALID = "Invalid"
        MQTT_BROKER_MESSAGES = "MqttBrokerMessages"
        TWIN_CHANGE_EVENTS = "TwinChangeEvents"


    class azure.mgmt.iothub.models.RoutingStorageContainerProperties(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        batch_frequency_in_seconds: Optional[int]
        connection_string: Optional[str]
        container_name: str
        encoding: Optional[Union[str, RoutingStorageContainerPropertiesEncoding]]
        endpoint_uri: Optional[str]
        file_name_format: Optional[str]
        id: Optional[str]
        identity: Optional[ManagedIdentity]
        max_chunk_size_in_bytes: Optional[int]
        name: str
        resource_group: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                batch_frequency_in_seconds: Optional[int] = ..., 
                connection_string: Optional[str] = ..., 
                container_name: str, 
                encoding: Optional[Union[str, RoutingStorageContainerPropertiesEncoding]] = ..., 
                endpoint_uri: Optional[str] = ..., 
                file_name_format: Optional[str] = ..., 
                id: Optional[str] = ..., 
                identity: Optional[ManagedIdentity] = ..., 
                max_chunk_size_in_bytes: Optional[int] = ..., 
                name: str, 
                resource_group: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingStorageContainerPropertiesEncoding(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVRO = "Avro"
        AVRO_DEFLATE = "AvroDeflate"
        JSON = "JSON"


    class azure.mgmt.iothub.models.RoutingTwin(_Model):
        properties: Optional[RoutingTwinProperties]
        tags: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoutingTwinProperties] = ..., 
                tags: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.RoutingTwinProperties(_Model):
        desired: Optional[dict[str, Any]]
        reported: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                desired: Optional[dict[str, Any]] = ..., 
                reported: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.SharedAccessSignatureAuthorizationRule(_Model):
        key_name: str
        primary_key: Optional[str]
        rights: Union[str, AccessRights]
        secondary_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_name: str, 
                primary_key: Optional[str] = ..., 
                rights: Union[str, AccessRights], 
                secondary_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.StorageEndpointProperties(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        connection_string: str
        container_name: str
        identity: Optional[ManagedIdentity]
        sas_ttl_as_iso8601: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                connection_string: str, 
                container_name: str, 
                identity: Optional[ManagedIdentity] = ..., 
                sas_ttl_as_iso8601: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.SystemData(_Model):
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


    class azure.mgmt.iothub.models.TagsResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.TestAllRoutesInput(_Model):
        message: Optional[RoutingMessage]
        routing_source: Optional[Union[str, RoutingSource]]
        twin: Optional[RoutingTwin]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[RoutingMessage] = ..., 
                routing_source: Optional[Union[str, RoutingSource]] = ..., 
                twin: Optional[RoutingTwin] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.TestAllRoutesResult(_Model):
        routes: Optional[list[MatchedRoute]]

        @overload
        def __init__(
                self, 
                *, 
                routes: Optional[list[MatchedRoute]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.TestResultStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"
        UNDEFINED = "undefined"


    class azure.mgmt.iothub.models.TestRouteInput(_Model):
        message: Optional[RoutingMessage]
        route: RouteProperties
        twin: Optional[RoutingTwin]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[RoutingMessage] = ..., 
                route: RouteProperties, 
                twin: Optional[RoutingTwin] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.TestRouteResult(_Model):
        details: Optional[TestRouteResultDetails]
        result: Optional[Union[str, TestResultStatus]]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[TestRouteResultDetails] = ..., 
                result: Optional[Union[str, TestResultStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.TestRouteResultDetails(_Model):
        compilation_errors: Optional[list[RouteCompilationError]]

        @overload
        def __init__(
                self, 
                *, 
                compilation_errors: Optional[list[RouteCompilationError]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.TrackedResource(Resource):
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


    class azure.mgmt.iothub.models.UserSubscriptionQuota(_Model):
        current_value: Optional[int]
        id: Optional[str]
        limit: Optional[int]
        name: Optional[Name]
        type: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[Name] = ..., 
                type: Optional[str] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iothub.models.UserSubscriptionQuotaListResult(_Model):
        next_link: Optional[str]
        value: Optional[list[UserSubscriptionQuota]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[UserSubscriptionQuota]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.iothub.operations

    class azure.mgmt.iothub.operations.CertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_description: CertificateDescription, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_description: CertificateDescription, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_description: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def generate_verification_code(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateWithNonceDescription: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @distributed_trace
        def list_by_iot_hub(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> CertificateListDescription: ...

        @overload
        def verify(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_verification_body: CertificateVerificationDescription, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @overload
        def verify(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_verification_body: CertificateVerificationDescription, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateDescription: ...

        @overload
        def verify(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                certificate_verification_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> CertificateDescription: ...


    class azure.mgmt.iothub.operations.IotHubOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_manual_failover(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                failover_input: FailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_manual_failover(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                failover_input: FailoverInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_manual_failover(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                failover_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.iothub.operations.IotHubResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_description: IotHubDescription, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[IotHubDescription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_description: IotHubDescription, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[IotHubDescription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_description: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[IotHubDescription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[IotHubDescription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IotHubDescription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IotHubDescription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                iot_hub_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IotHubDescription]: ...

        @overload
        def check_name_availability(
                self, 
                operation_inputs: OperationInputs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IotHubNameAvailabilityInfo: ...

        @overload
        def check_name_availability(
                self, 
                operation_inputs: OperationInputs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IotHubNameAvailabilityInfo: ...

        @overload
        def check_name_availability(
                self, 
                operation_inputs: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IotHubNameAvailabilityInfo: ...

        @overload
        def create_event_hub_consumer_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                name: str, 
                consumer_group_body: EventHubConsumerGroupBodyDescription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventHubConsumerGroupInfo: ...

        @overload
        def create_event_hub_consumer_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                name: str, 
                consumer_group_body: EventHubConsumerGroupBodyDescription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventHubConsumerGroupInfo: ...

        @overload
        def create_event_hub_consumer_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                name: str, 
                consumer_group_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EventHubConsumerGroupInfo: ...

        @distributed_trace
        def delete_event_hub_consumer_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def export_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_devices_parameters: ExportDevicesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        def export_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_devices_parameters: ExportDevicesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        def export_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                export_devices_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> IotHubDescription: ...

        @distributed_trace
        def get_endpoint_health(
                self, 
                resource_group_name: str, 
                iot_hub_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EndpointHealthData]: ...

        @distributed_trace
        def get_event_hub_consumer_group(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                name: str, 
                **kwargs: Any
            ) -> EventHubConsumerGroupInfo: ...

        @distributed_trace
        def get_job(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> JobResponse: ...

        @distributed_trace
        def get_keys_for_key_name(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                key_name: str, 
                **kwargs: Any
            ) -> SharedAccessSignatureAuthorizationRule: ...

        @distributed_trace
        def get_quota_metrics(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IotHubQuotaMetricInfo]: ...

        @distributed_trace
        def get_stats(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> RegistryStatistics: ...

        @distributed_trace
        def get_valid_skus(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IotHubSkuDescription]: ...

        @overload
        def import_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                import_devices_parameters: ImportDevicesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        def import_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                import_devices_parameters: ImportDevicesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @overload
        def import_devices(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                import_devices_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IotHubDescription]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[IotHubDescription]: ...

        @distributed_trace
        def list_event_hub_consumer_groups(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                event_hub_endpoint_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EventHubConsumerGroupInfo]: ...

        @distributed_trace
        def list_jobs(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[JobResponse]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SharedAccessSignatureAuthorizationRule]: ...

        @overload
        def test_all_routes(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: TestAllRoutesInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestAllRoutesResult: ...

        @overload
        def test_all_routes(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: TestAllRoutesInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestAllRoutesResult: ...

        @overload
        def test_all_routes(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestAllRoutesResult: ...

        @overload
        def test_route(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: TestRouteInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestRouteResult: ...

        @overload
        def test_route(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: TestRouteInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestRouteResult: ...

        @overload
        def test_route(
                self, 
                iot_hub_name: str, 
                resource_group_name: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestRouteResult: ...


    class azure.mgmt.iothub.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.iothub.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> List[PrivateEndpointConnection]: ...


    class azure.mgmt.iothub.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                group_id: str, 
                **kwargs: Any
            ) -> GroupIdInformation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResources: ...


    class azure.mgmt.iothub.operations.ResourceProviderCommonOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_subscription_quota(self, **kwargs: Any) -> UserSubscriptionQuotaListResult: ...


namespace azure.mgmt.iothub.types

    class azure.mgmt.iothub.types.ArmIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, ArmUserIdentity]
        user_assigned_identities: dict[str, ArmUserIdentity]


    class azure.mgmt.iothub.types.ArmUserIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.iothub.types.CertificateDescription(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('CertificateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: CertificateProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iothub.types.CertificateProperties(TypedDict, total=False):
        key "certificate": str
        key "created": str
        key "expiry": str
        key "isVerified": bool
        key "policyResourceId": str
        key "subject": str
        key "thumbprint": str
        key "updated": str
        certificate: str
        created: str
        expiry: str
        is_verified: bool
        policy_resource_id: str
        subject: str
        thumbprint: str
        updated: str


    class azure.mgmt.iothub.types.CertificateVerificationDescription(TypedDict, total=False):
        key "certificate": str
        certificate: str


    class azure.mgmt.iothub.types.CloudToDeviceProperties(TypedDict, total=False):
        key "defaultTtlAsIso8601": str
        key "feedback": ForwardRef('FeedbackProperties', module='types')
        key "maxDeliveryCount": int
        default_ttl_as_iso8601: str
        feedback: FeedbackProperties
        max_delivery_count: int


    class azure.mgmt.iothub.types.DeviceRegistry(TypedDict, total=False):
        key "identityResourceId": str
        key "namespaceResourceId": str
        identity_resource_id: str
        namespace_resource_id: str


    class azure.mgmt.iothub.types.EncryptionPropertiesDescription(TypedDict, total=False):
        key "keySource": str
        keyVaultProperties: list[KeyVaultKeyProperties]
        key_source: str
        key_vault_properties: list[KeyVaultKeyProperties]


    class azure.mgmt.iothub.types.EnrichmentProperties(TypedDict, total=False):
        key "endpointNames": Required[list[str]]
        key "key": Required[str]
        key "value": Required[str]
        endpoint_names: list[str]
        key: str
        value: str


    class azure.mgmt.iothub.types.EventHubConsumerGroupBodyDescription(TypedDict, total=False):
        key "properties": Required[EventHubConsumerGroupName]
        properties: EventHubConsumerGroupName


    class azure.mgmt.iothub.types.EventHubConsumerGroupName(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.iothub.types.EventHubProperties(TypedDict, total=False):
        key "endpoint": str
        key "partitionCount": int
        key "path": str
        key "retentionTimeInDays": int
        endpoint: str
        partitionIds: list[str]
        partition_count: int
        partition_ids: list[str]
        path: str
        retention_time_in_days: int


    class azure.mgmt.iothub.types.ExportDevicesRequest(TypedDict, total=False):
        key "authenticationType": Union[str, AuthenticationType]
        key "configurationsBlobName": str
        key "excludeKeys": Required[bool]
        key "exportBlobContainerUri": Required[str]
        key "exportBlobName": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "includeConfigurations": bool
        authentication_type: Union[str, AuthenticationType]
        configurations_blob_name: str
        exclude_keys: bool
        export_blob_container_uri: str
        export_blob_name: str
        identity: ManagedIdentity
        include_configurations: bool


    class azure.mgmt.iothub.types.FailoverInput(TypedDict, total=False):
        key "failoverRegion": Required[str]
        failover_region: str


    class azure.mgmt.iothub.types.FallbackRouteProperties(TypedDict, total=False):
        key "condition": str
        key "endpointNames": Required[list[str]]
        key "isEnabled": Required[bool]
        key "name": str
        key "source": Required[Union[str, RoutingSource]]
        condition: str
        endpoint_names: list[str]
        is_enabled: bool
        name: str
        source: Union[str, RoutingSource]


    class azure.mgmt.iothub.types.FeedbackProperties(TypedDict, total=False):
        key "lockDurationAsIso8601": str
        key "maxDeliveryCount": int
        key "ttlAsIso8601": str
        lock_duration_as_iso8601: str
        max_delivery_count: int
        ttl_as_iso8601: str


    class azure.mgmt.iothub.types.ImportDevicesRequest(TypedDict, total=False):
        key "authenticationType": Union[str, AuthenticationType]
        key "configurationsBlobName": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "includeConfigurations": bool
        key "inputBlobContainerUri": Required[str]
        key "inputBlobName": str
        key "outputBlobContainerUri": Required[str]
        key "outputBlobName": str
        authentication_type: Union[str, AuthenticationType]
        configurations_blob_name: str
        identity: ManagedIdentity
        include_configurations: bool
        input_blob_container_uri: str
        input_blob_name: str
        output_blob_container_uri: str
        output_blob_name: str


    class azure.mgmt.iothub.types.IotHubDescription(TrackedResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('ArmIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('IotHubProperties', module='types')
        key "sku": Required[IotHubSkuInfo]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: ArmIdentity
        location: str
        name: str
        properties: IotHubProperties
        sku: IotHubSkuInfo
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.iothub.types.IotHubDetails(TypedDict, total=False):
        key "gatewayVersion": Union[str, GatewayVersion]
        gateway_version: Union[str, GatewayVersion]


    class azure.mgmt.iothub.types.IotHubLocationDescription(TypedDict, total=False):
        key "location": str
        key "role": Union[str, IotHubReplicaRoleType]
        location: str
        role: Union[str, IotHubReplicaRoleType]


    class azure.mgmt.iothub.types.IotHubProperties(TypedDict, total=False):
        key "cloudToDevice": ForwardRef('CloudToDeviceProperties', module='types')
        key "comments": str
        key "deviceHostName": str
        key "deviceRegistry": ForwardRef('DeviceRegistry', module='types')
        key "deviceStreams": ForwardRef('IotHubPropertiesDeviceStreams', module='types')
        key "disableDeviceSAS": bool
        key "disableLocalAuth": bool
        key "disableModuleSAS": bool
        key "enableDataResidency": bool
        key "enableFileUploadNotifications": bool
        key "encryption": ForwardRef('EncryptionPropertiesDescription', module='types')
        key "features": Union[str, Capabilities]
        key "hostName": str
        key "iotHubDetails": ForwardRef('IotHubDetails', module='types')
        key "ipVersion": Union[str, IpVersion]
        key "minTlsVersion": str
        key "networkRuleSets": ForwardRef('NetworkRuleSetProperties', module='types')
        key "provisioningState": str
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "restrictOutboundNetworkAccess": bool
        key "rootCertificate": ForwardRef('RootCertificateProperties', module='types')
        key "routing": ForwardRef('RoutingProperties', module='types')
        key "serviceHostName": str
        key "state": str
        allowedFqdnList: list[str]
        allowed_fqdn_list: list[str]
        authorizationPolicies: list[SharedAccessSignatureAuthorizationRule]
        authorization_policies: list[SharedAccessSignatureAuthorizationRule]
        cloud_to_device: CloudToDeviceProperties
        comments: str
        device_host_name: str
        device_registry: DeviceRegistry
        device_streams: IotHubPropertiesDeviceStreams
        disable_device_sas: bool
        disable_local_auth: bool
        disable_module_sas: bool
        enable_data_residency: bool
        enable_file_upload_notifications: bool
        encryption: EncryptionPropertiesDescription
        eventHubEndpoints: dict[str, EventHubProperties]
        event_hub_endpoints: dict[str, EventHubProperties]
        features: Union[str, Capabilities]
        host_name: str
        iot_hub_details: IotHubDetails
        ipFilterRules: list[IpFilterRule]
        ip_filter_rules: list[IpFilterRule]
        ip_version: Union[str, IpVersion]
        locations: list[IotHubLocationDescription]
        messagingEndpoints: dict[str, MessagingEndpointProperties]
        messaging_endpoints: dict[str, MessagingEndpointProperties]
        min_tls_version: str
        network_rule_sets: NetworkRuleSetProperties
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        public_network_access: Union[str, PublicNetworkAccess]
        restrict_outbound_network_access: bool
        root_certificate: RootCertificateProperties
        routing: RoutingProperties
        service_host_name: str
        state: str
        storageEndpoints: dict[str, StorageEndpointProperties]
        storage_endpoints: dict[str, StorageEndpointProperties]


    class azure.mgmt.iothub.types.IotHubPropertiesDeviceStreams(TypedDict, total=False):
        streamingEndpoints: list[str]
        streaming_endpoints: list[str]


    class azure.mgmt.iothub.types.IotHubSkuInfo(TypedDict, total=False):
        key "capacity": int
        key "name": Required[Union[str, IotHubSku]]
        key "tier": Union[str, IotHubSkuTier]
        capacity: int
        name: Union[str, IotHubSku]
        tier: Union[str, IotHubSkuTier]


    class azure.mgmt.iothub.types.IpFilterRule(TypedDict, total=False):
        key "action": Required[Union[str, IpFilterActionType]]
        key "filterName": Required[str]
        key "ipMask": Required[str]
        action: Union[str, IpFilterActionType]
        filter_name: str
        ip_mask: str


    class azure.mgmt.iothub.types.KeyVaultKeyProperties(TypedDict, total=False):
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "keyIdentifier": str
        identity: ManagedIdentity
        key_identifier: str


    class azure.mgmt.iothub.types.ManagedIdentity(TypedDict, total=False):
        key "userAssignedIdentity": str
        user_assigned_identity: str


    class azure.mgmt.iothub.types.MessagingEndpointProperties(TypedDict, total=False):
        key "lockDurationAsIso8601": str
        key "maxDeliveryCount": int
        key "ttlAsIso8601": str
        lock_duration_as_iso8601: str
        max_delivery_count: int
        ttl_as_iso8601: str


    class azure.mgmt.iothub.types.NetworkRuleSetIpRule(TypedDict, total=False):
        key "action": Union[str, NetworkRuleIPAction]
        key "filterName": Required[str]
        key "ipMask": Required[str]
        action: Union[str, NetworkRuleIPAction]
        filter_name: str
        ip_mask: str


    class azure.mgmt.iothub.types.NetworkRuleSetProperties(TypedDict, total=False):
        key "applyToBuiltInEventHubEndpoint": Required[bool]
        key "defaultAction": Union[str, DefaultAction]
        key "ipRules": Required[list[NetworkRuleSetIpRule]]
        apply_to_built_in_event_hub_endpoint: bool
        default_action: Union[str, DefaultAction]
        ip_rules: list[NetworkRuleSetIpRule]


    class azure.mgmt.iothub.types.OperationInputs(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.iothub.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.iothub.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[PrivateEndpointConnectionProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iothub.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState


    class azure.mgmt.iothub.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": Required[str]
        key "status": Required[Union[str, PrivateLinkServiceConnectionStatus]]
        actions_required: str
        description: str
        status: Union[str, PrivateLinkServiceConnectionStatus]


    class azure.mgmt.iothub.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.iothub.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.iothub.types.RootCertificateProperties(TypedDict, total=False):
        key "enableRootCertificateV2": bool
        key "lastUpdatedTimeUtc": str
        enable_root_certificate_v2: bool
        last_updated_time_utc: str


    class azure.mgmt.iothub.types.RouteProperties(TypedDict, total=False):
        key "condition": str
        key "endpointNames": Required[list[str]]
        key "isEnabled": Required[bool]
        key "name": Required[str]
        key "source": Required[Union[str, RoutingSource]]
        condition: str
        endpoint_names: list[str]
        is_enabled: bool
        name: str
        source: Union[str, RoutingSource]


    class azure.mgmt.iothub.types.RoutingCosmosDBSqlApiProperties(TypedDict, total=False):
        key "authenticationType": Union[str, AuthenticationType]
        key "containerName": Required[str]
        key "databaseName": Required[str]
        key "endpointUri": Required[str]
        key "id": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "name": Required[str]
        key "partitionKeyName": str
        key "partitionKeyTemplate": str
        key "primaryKey": str
        key "resourceGroup": str
        key "secondaryKey": str
        key "subscriptionId": str
        authentication_type: Union[str, AuthenticationType]
        container_name: str
        database_name: str
        endpoint_uri: str
        id: str
        identity: ManagedIdentity
        name: str
        partition_key_name: str
        partition_key_template: str
        primary_key: str
        resource_group: str
        secondary_key: str
        subscription_id: str


    class azure.mgmt.iothub.types.RoutingEndpoints(TypedDict, total=False):
        cosmosDBSqlContainers: list[RoutingCosmosDBSqlApiProperties]
        cosmos_db_sql_containers: list[RoutingCosmosDBSqlApiProperties]
        eventHubs: list[RoutingEventHubProperties]
        eventStreams: list[RoutingEventStreamProperties]
        event_hubs: list[RoutingEventHubProperties]
        event_streams: list[RoutingEventStreamProperties]
        serviceBusQueues: list[RoutingServiceBusQueueEndpointProperties]
        serviceBusTopics: list[RoutingServiceBusTopicEndpointProperties]
        service_bus_queues: list[RoutingServiceBusQueueEndpointProperties]
        service_bus_topics: list[RoutingServiceBusTopicEndpointProperties]
        storageContainers: list[RoutingStorageContainerProperties]
        storage_containers: list[RoutingStorageContainerProperties]


    class azure.mgmt.iothub.types.RoutingEventHubProperties(TypedDict, total=False):
        key "authenticationType": Union[str, AuthenticationType]
        key "connectionString": str
        key "endpointUri": str
        key "entityPath": str
        key "id": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "name": Required[str]
        key "resourceGroup": str
        key "subscriptionId": str
        authentication_type: Union[str, AuthenticationType]
        connection_string: str
        endpoint_uri: str
        entity_path: str
        id: str
        identity: ManagedIdentity
        name: str
        resource_group: str
        subscription_id: str


    class azure.mgmt.iothub.types.RoutingEventStreamProperties(TypedDict, total=False):
        key "authenticationType": Union[str, EventStreamAuthenticationType]
        key "endpointUri": Required[str]
        key "entityPath": Required[str]
        key "eventStreamId": str
        key "id": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "name": Required[str]
        key "sourceId": str
        key "workspaceId": str
        authentication_type: Union[str, EventStreamAuthenticationType]
        endpoint_uri: str
        entity_path: str
        event_stream_id: str
        id: str
        identity: ManagedIdentity
        name: str
        source_id: str
        workspace_id: str


    class azure.mgmt.iothub.types.RoutingMessage(TypedDict, total=False):
        key "body": str
        appProperties: dict[str, str]
        app_properties: dict[str, str]
        body: str
        systemProperties: dict[str, str]
        system_properties: dict[str, str]


    class azure.mgmt.iothub.types.RoutingProperties(TypedDict, total=False):
        key "endpoints": ForwardRef('RoutingEndpoints', module='types')
        key "fallbackRoute": ForwardRef('FallbackRouteProperties', module='types')
        endpoints: RoutingEndpoints
        enrichments: list[EnrichmentProperties]
        fallback_route: FallbackRouteProperties
        routes: list[RouteProperties]


    class azure.mgmt.iothub.types.RoutingServiceBusQueueEndpointProperties(TypedDict, total=False):
        key "authenticationType": Union[str, AuthenticationType]
        key "connectionString": str
        key "endpointUri": str
        key "entityPath": str
        key "id": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "name": Required[str]
        key "resourceGroup": str
        key "subscriptionId": str
        authentication_type: Union[str, AuthenticationType]
        connection_string: str
        endpoint_uri: str
        entity_path: str
        id: str
        identity: ManagedIdentity
        name: str
        resource_group: str
        subscription_id: str


    class azure.mgmt.iothub.types.RoutingServiceBusTopicEndpointProperties(TypedDict, total=False):
        key "authenticationType": Union[str, AuthenticationType]
        key "connectionString": str
        key "endpointUri": str
        key "entityPath": str
        key "id": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "name": Required[str]
        key "resourceGroup": str
        key "subscriptionId": str
        authentication_type: Union[str, AuthenticationType]
        connection_string: str
        endpoint_uri: str
        entity_path: str
        id: str
        identity: ManagedIdentity
        name: str
        resource_group: str
        subscription_id: str


    class azure.mgmt.iothub.types.RoutingStorageContainerProperties(TypedDict, total=False):
        key "authenticationType": Union[str, AuthenticationType]
        key "batchFrequencyInSeconds": int
        key "connectionString": str
        key "containerName": Required[str]
        key "encoding": Union[str, RoutingStorageContainerPropertiesEncoding]
        key "endpointUri": str
        key "fileNameFormat": str
        key "id": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "maxChunkSizeInBytes": int
        key "name": Required[str]
        key "resourceGroup": str
        key "subscriptionId": str
        authentication_type: Union[str, AuthenticationType]
        batch_frequency_in_seconds: int
        connection_string: str
        container_name: str
        encoding: Union[str, RoutingStorageContainerPropertiesEncoding]
        endpoint_uri: str
        file_name_format: str
        id: str
        identity: ManagedIdentity
        max_chunk_size_in_bytes: int
        name: str
        resource_group: str
        subscription_id: str


    class azure.mgmt.iothub.types.RoutingTwin(TypedDict, total=False):
        key "properties": ForwardRef('RoutingTwinProperties', module='types')
        properties: RoutingTwinProperties
        tags: dict[str, Any]


    class azure.mgmt.iothub.types.RoutingTwinProperties(TypedDict, total=False):
        desired: dict[str, Any]
        reported: dict[str, Any]


    class azure.mgmt.iothub.types.SharedAccessSignatureAuthorizationRule(TypedDict, total=False):
        key "keyName": Required[str]
        key "primaryKey": str
        key "rights": Required[Union[str, AccessRights]]
        key "secondaryKey": str
        key_name: str
        primary_key: str
        rights: Union[str, AccessRights]
        secondary_key: str


    class azure.mgmt.iothub.types.StorageEndpointProperties(TypedDict, total=False):
        key "authenticationType": Union[str, AuthenticationType]
        key "connectionString": Required[str]
        key "containerName": Required[str]
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "sasTtlAsIso8601": str
        authentication_type: Union[str, AuthenticationType]
        connection_string: str
        container_name: str
        identity: ManagedIdentity
        sas_ttl_as_iso8601: str


    class azure.mgmt.iothub.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.iothub.types.TagsResource(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.iothub.types.TestAllRoutesInput(TypedDict, total=False):
        key "message": ForwardRef('RoutingMessage', module='types')
        key "routingSource": Union[str, RoutingSource]
        key "twin": ForwardRef('RoutingTwin', module='types')
        message: RoutingMessage
        routing_source: Union[str, RoutingSource]
        twin: RoutingTwin


    class azure.mgmt.iothub.types.TestRouteInput(TypedDict, total=False):
        key "message": ForwardRef('RoutingMessage', module='types')
        key "route": Required[RouteProperties]
        key "twin": ForwardRef('RoutingTwin', module='types')
        message: RoutingMessage
        route: RouteProperties
        twin: RoutingTwin


    class azure.mgmt.iothub.types.TrackedResource(Resource):
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


```