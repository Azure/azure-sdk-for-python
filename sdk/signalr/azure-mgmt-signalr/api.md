```py
namespace azure.mgmt.signalr

    class azure.mgmt.signalr.SignalRManagementClient: implements ContextManager 
        operations: Operations
        signal_r: SignalROperations
        signal_rcustom_certificates: SignalRCustomCertificatesOperations
        signal_rcustom_domains: SignalRCustomDomainsOperations
        signal_rprivate_endpoint_connections: SignalRPrivateEndpointConnectionsOperations
        signal_rprivate_link_resources: SignalRPrivateLinkResourcesOperations
        signal_rreplica_shared_private_link_resources: SignalRReplicaSharedPrivateLinkResourcesOperations
        signal_rreplicas: SignalRReplicasOperations
        signal_rshared_private_link_resources: SignalRSharedPrivateLinkResourcesOperations
        usages: UsagesOperations

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


namespace azure.mgmt.signalr.aio

    class azure.mgmt.signalr.aio.SignalRManagementClient: implements AsyncContextManager 
        operations: Operations
        signal_r: SignalROperations
        signal_rcustom_certificates: SignalRCustomCertificatesOperations
        signal_rcustom_domains: SignalRCustomDomainsOperations
        signal_rprivate_endpoint_connections: SignalRPrivateEndpointConnectionsOperations
        signal_rprivate_link_resources: SignalRPrivateLinkResourcesOperations
        signal_rreplica_shared_private_link_resources: SignalRReplicaSharedPrivateLinkResourcesOperations
        signal_rreplicas: SignalRReplicasOperations
        signal_rshared_private_link_resources: SignalRSharedPrivateLinkResourcesOperations
        usages: UsagesOperations

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


namespace azure.mgmt.signalr.aio.operations

    class azure.mgmt.signalr.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.signalr.aio.operations.SignalRCustomCertificatesOperations:

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
                certificate_name: str, 
                parameters: CustomCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomCertificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                parameters: CustomCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomCertificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomCertificate]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CustomCertificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CustomCertificate]: ...


    class azure.mgmt.signalr.aio.operations.SignalRCustomDomainsOperations:

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
                name: str, 
                parameters: CustomDomain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomain]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                parameters: CustomDomain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomain]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomain]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                **kwargs: Any
            ) -> CustomDomain: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CustomDomain]: ...


    class azure.mgmt.signalr.aio.operations.SignalROperations:

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
                parameters: SignalRResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalRResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: SignalRResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalRResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalRResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalRKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalRKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalRKeys]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: SignalRResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalRResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: SignalRResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalRResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalRResource]: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                parameters: NameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                parameters: NameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> SignalRResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SignalRResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SignalRResource]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> SignalRKeys: ...

        @distributed_trace_async
        async def list_replica_skus(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> SkuList: ...

        @distributed_trace_async
        async def list_skus(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> SkuList: ...


    class azure.mgmt.signalr.aio.operations.SignalRPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                private_endpoint_connection_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                private_endpoint_connection_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...

        @overload
        async def update(
                self, 
                private_endpoint_connection_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def update(
                self, 
                private_endpoint_connection_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def update(
                self, 
                private_endpoint_connection_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.signalr.aio.operations.SignalRPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.signalr.aio.operations.SignalRReplicaSharedPrivateLinkResourcesOperations:

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
                replica_name: str, 
                shared_private_link_resource_name: str, 
                parameters: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                shared_private_link_resource_name: str, 
                parameters: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                shared_private_link_resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                shared_private_link_resource_name: str, 
                **kwargs: Any
            ) -> SharedPrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedPrivateLinkResource]: ...


    class azure.mgmt.signalr.aio.operations.SignalRReplicasOperations:

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
                replica_name: str, 
                parameters: Replica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replica]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                parameters: Replica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replica]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replica]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                parameters: Replica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replica]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                parameters: Replica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replica]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replica]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> Replica: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Replica]: ...


    class azure.mgmt.signalr.aio.operations.SignalRSharedPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                shared_private_link_resource_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                shared_private_link_resource_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                shared_private_link_resource_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                shared_private_link_resource_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                shared_private_link_resource_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> SharedPrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedPrivateLinkResource]: ...


    class azure.mgmt.signalr.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SignalRUsage]: ...


namespace azure.mgmt.signalr.models

    class azure.mgmt.signalr.models.ACLAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.signalr.models.ApplicationFirewallSettings(_Model):
        client_connection_count_rules: Optional[list[ClientConnectionCountRule]]
        client_traffic_control_rules: Optional[list[ClientTrafficControlRule]]
        max_client_connection_lifetime_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                client_connection_count_rules: Optional[list[ClientConnectionCountRule]] = ..., 
                client_traffic_control_rules: Optional[list[ClientTrafficControlRule]] = ..., 
                max_client_connection_lifetime_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ClientConnectionCountRule(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ClientConnectionCountRuleDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE = "ThrottleByJwtCustomClaimRule"
        THROTTLE_BY_JWT_SIGNATURE_RULE = "ThrottleByJwtSignatureRule"
        THROTTLE_BY_USER_ID_RULE = "ThrottleByUserIdRule"


    class azure.mgmt.signalr.models.ClientTrafficControlRule(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ClientTrafficControlRuleDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRAFFIC_THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE = "TrafficThrottleByJwtCustomClaimRule"
        TRAFFIC_THROTTLE_BY_JWT_SIGNATURE_RULE = "TrafficThrottleByJwtSignatureRule"
        TRAFFIC_THROTTLE_BY_USER_ID_RULE = "TrafficThrottleByUserIdRule"


    class azure.mgmt.signalr.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.signalr.models.CustomCertificate(ProxyResource):
        id: str
        name: str
        properties: CustomCertificateProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: CustomCertificateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.signalr.models.CustomCertificateProperties(_Model):
        key_vault_base_uri: str
        key_vault_secret_name: str
        key_vault_secret_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_base_uri: str, 
                key_vault_secret_name: str, 
                key_vault_secret_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.CustomDomain(ProxyResource):
        id: str
        name: str
        properties: CustomDomainProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: CustomDomainProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.signalr.models.CustomDomainProperties(_Model):
        custom_certificate: ResourceReference
        domain_name: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                custom_certificate: ResourceReference, 
                domain_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.Dimension(_Model):
        display_name: Optional[str]
        internal_name: Optional[str]
        name: Optional[str]
        to_be_exported_for_shoebox: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                internal_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                to_be_exported_for_shoebox: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.signalr.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.signalr.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.FeatureFlags(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENABLE_CONNECTIVITY_LOGS = "EnableConnectivityLogs"
        ENABLE_LIVE_TRACE = "EnableLiveTrace"
        ENABLE_MESSAGING_LOGS = "EnableMessagingLogs"
        SERVICE_MODE = "ServiceMode"


    class azure.mgmt.signalr.models.IPRule(_Model):
        action: Optional[Union[str, ACLAction]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, ACLAction]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SALT = "Salt"
        SECONDARY = "Secondary"


    class azure.mgmt.signalr.models.LiveTraceCategory(_Model):
        enabled: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.LiveTraceConfiguration(_Model):
        categories: Optional[list[LiveTraceCategory]]
        enabled: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                categories: Optional[list[LiveTraceCategory]] = ..., 
                enabled: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.LogSpecification(_Model):
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ManagedIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ManagedIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentityProperty]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentityProperty]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ManagedIdentitySettings(_Model):
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.signalr.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        category: Optional[str]
        dimensions: Optional[list[Dimension]]
        display_description: Optional[str]
        display_name: Optional[str]
        fill_gap_with_zero: Optional[str]
        name: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                category: Optional[str] = ..., 
                dimensions: Optional[list[Dimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                fill_gap_with_zero: Optional[str] = ..., 
                name: Optional[str] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.NameAvailability(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.NameAvailabilityParameters(_Model):
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.NetworkACL(_Model):
        allow: Optional[list[Union[str, SignalRRequestType]]]
        deny: Optional[list[Union[str, SignalRRequestType]]]

        @overload
        def __init__(
                self, 
                *, 
                allow: Optional[list[Union[str, SignalRRequestType]]] = ..., 
                deny: Optional[list[Union[str, SignalRRequestType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[OperationProperties]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[OperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.PrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.PrivateEndpointACL(NetworkACL):
        allow: Union[list[str, SignalRRequestType]]
        deny: Union[list[str, SignalRRequestType]]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                allow: Optional[list[Union[str, SignalRRequestType]]] = ..., 
                deny: Optional[list[Union[str, SignalRRequestType]]] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.signalr.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.signalr.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]
        shareable_private_link_resource_types: Optional[list[ShareablePrivateLinkResourceType]]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                required_members: Optional[list[str]] = ..., 
                required_zone_names: Optional[list[str]] = ..., 
                shareable_private_link_resource_types: Optional[list[ShareablePrivateLinkResourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateLinkServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateLinkServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.PrivateLinkServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.signalr.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.signalr.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.signalr.models.RegenerateKeyParameters(_Model):
        key_type: Optional[Union[str, KeyType]]

        @overload
        def __init__(
                self, 
                *, 
                key_type: Optional[Union[str, KeyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.Replica(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ReplicaProperties]
        sku: Optional[ResourceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ReplicaProperties] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.signalr.models.ReplicaProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        region_endpoint_enabled: Optional[str]
        resource_stopped: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                region_endpoint_enabled: Optional[str] = ..., 
                resource_stopped: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.signalr.models.ResourceLogCategory(_Model):
        enabled: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ResourceLogConfiguration(_Model):
        categories: Optional[list[ResourceLogCategory]]

        @overload
        def __init__(
                self, 
                *, 
                categories: Optional[list[ResourceLogCategory]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ResourceReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ResourceSku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[Union[str, SignalRSkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: str, 
                tier: Optional[Union[str, SignalRSkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.RouteSettings(_Model):
        connection_balance_weight: Optional[int]
        latency_weight: Optional[int]
        server_balance_weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                connection_balance_weight: Optional[int] = ..., 
                latency_weight: Optional[int] = ..., 
                server_balance_weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.signalr.models.ServerlessSettings(_Model):
        connection_timeout_in_seconds: Optional[int]
        keep_alive_interval_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                connection_timeout_in_seconds: Optional[int] = ..., 
                keep_alive_interval_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ServerlessUpstreamSettings(_Model):
        templates: Optional[list[UpstreamTemplate]]

        @overload
        def __init__(
                self, 
                *, 
                templates: Optional[list[UpstreamTemplate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ServiceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RAW_WEB_SOCKETS = "RawWebSockets"
        SIGNAL_R = "SignalR"


    class azure.mgmt.signalr.models.ServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[LogSpecification]] = ..., 
                metric_specifications: Optional[list[MetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ShareablePrivateLinkResourceProperties(_Model):
        description: Optional[str]
        group_id: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                group_id: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ShareablePrivateLinkResourceType(_Model):
        name: Optional[str]
        properties: Optional[ShareablePrivateLinkResourceProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[ShareablePrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.SharedPrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SharedPrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SharedPrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.signalr.models.SharedPrivateLinkResourceProperties(_Model):
        fqdns: Optional[list[str]]
        group_id: str
        private_link_resource_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        request_message: Optional[str]
        status: Optional[Union[str, SharedPrivateLinkResourceStatus]]

        @overload
        def __init__(
                self, 
                *, 
                fqdns: Optional[list[str]] = ..., 
                group_id: str, 
                private_link_resource_id: str, 
                request_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.SharedPrivateLinkResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"
        TIMEOUT = "Timeout"


    class azure.mgmt.signalr.models.SignalRCorsSettings(_Model):
        allowed_origins: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_origins: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.SignalRFeature(_Model):
        flag: Union[str, FeatureFlags]
        properties: Optional[dict[str, str]]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                flag: Union[str, FeatureFlags], 
                properties: Optional[dict[str, str]] = ..., 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.SignalRKeys(_Model):
        primary_connection_string: Optional[str]
        primary_key: Optional[str]
        secondary_connection_string: Optional[str]
        secondary_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_connection_string: Optional[str] = ..., 
                primary_key: Optional[str] = ..., 
                secondary_connection_string: Optional[str] = ..., 
                secondary_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.SignalRNetworkACLs(_Model):
        default_action: Optional[Union[str, ACLAction]]
        ip_rules: Optional[list[IPRule]]
        private_endpoints: Optional[list[PrivateEndpointACL]]
        public_network: Optional[NetworkACL]

        @overload
        def __init__(
                self, 
                *, 
                default_action: Optional[Union[str, ACLAction]] = ..., 
                ip_rules: Optional[list[IPRule]] = ..., 
                private_endpoints: Optional[list[PrivateEndpointACL]] = ..., 
                public_network: Optional[NetworkACL] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.SignalRProperties(_Model):
        application_firewall: Optional[ApplicationFirewallSettings]
        cors: Optional[SignalRCorsSettings]
        disable_aad_auth: Optional[bool]
        disable_local_auth: Optional[bool]
        external_ip: Optional[str]
        features: Optional[list[SignalRFeature]]
        host_name: Optional[str]
        host_name_prefix: Optional[str]
        live_trace_configuration: Optional[LiveTraceConfiguration]
        network_ac_ls: Optional[SignalRNetworkACLs]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[str]
        public_port: Optional[int]
        region_endpoint_enabled: Optional[str]
        resource_log_configuration: Optional[ResourceLogConfiguration]
        resource_stopped: Optional[str]
        route_settings: Optional[RouteSettings]
        server_port: Optional[int]
        serverless: Optional[ServerlessSettings]
        shared_private_link_resources: Optional[list[SharedPrivateLinkResource]]
        tls: Optional[SignalRTlsSettings]
        upstream: Optional[ServerlessUpstreamSettings]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_firewall: Optional[ApplicationFirewallSettings] = ..., 
                cors: Optional[SignalRCorsSettings] = ..., 
                disable_aad_auth: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                features: Optional[list[SignalRFeature]] = ..., 
                live_trace_configuration: Optional[LiveTraceConfiguration] = ..., 
                network_ac_ls: Optional[SignalRNetworkACLs] = ..., 
                public_network_access: Optional[str] = ..., 
                region_endpoint_enabled: Optional[str] = ..., 
                resource_log_configuration: Optional[ResourceLogConfiguration] = ..., 
                resource_stopped: Optional[str] = ..., 
                route_settings: Optional[RouteSettings] = ..., 
                serverless: Optional[ServerlessSettings] = ..., 
                tls: Optional[SignalRTlsSettings] = ..., 
                upstream: Optional[ServerlessUpstreamSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.SignalRRequestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_CONNECTION = "ClientConnection"
        RESTAPI = "RESTAPI"
        SERVER_CONNECTION = "ServerConnection"
        TRACE = "Trace"


    class azure.mgmt.signalr.models.SignalRResource(TrackedResource):
        id: str
        identity: Optional[ManagedIdentity]
        kind: Optional[Union[str, ServiceKind]]
        location: str
        name: str
        properties: Optional[SignalRProperties]
        sku: Optional[ResourceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedIdentity] = ..., 
                kind: Optional[Union[str, ServiceKind]] = ..., 
                location: str, 
                properties: Optional[SignalRProperties] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.signalr.models.SignalRSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.signalr.models.SignalRTlsSettings(_Model):
        client_cert_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                client_cert_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.SignalRUsage(_Model):
        current_value: Optional[int]
        id: Optional[str]
        limit: Optional[int]
        name: Optional[SignalRUsageName]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[SignalRUsageName] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.SignalRUsageName(_Model):
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


    class azure.mgmt.signalr.models.Sku(_Model):
        capacity: Optional[SkuCapacity]
        resource_type: Optional[str]
        sku: Optional[ResourceSku]


    class azure.mgmt.signalr.models.SkuCapacity(_Model):
        allowed_values: Optional[list[int]]
        default: Optional[int]
        maximum: Optional[int]
        minimum: Optional[int]
        scale_type: Optional[Union[str, ScaleType]]


    class azure.mgmt.signalr.models.SkuList(_Model):
        next_link: Optional[str]
        value: Optional[list[Sku]]


    class azure.mgmt.signalr.models.SystemData(_Model):
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


    class azure.mgmt.signalr.models.ThrottleByJwtCustomClaimRule(ClientConnectionCountRule, discriminator='ThrottleByJwtCustomClaimRule'):
        claim_name: str
        max_count: Optional[int]
        type: Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE]

        @overload
        def __init__(
                self, 
                *, 
                claim_name: str, 
                max_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ThrottleByJwtSignatureRule(ClientConnectionCountRule, discriminator='ThrottleByJwtSignatureRule'):
        max_count: Optional[int]
        type: Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_JWT_SIGNATURE_RULE]

        @overload
        def __init__(
                self, 
                *, 
                max_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.ThrottleByUserIdRule(ClientConnectionCountRule, discriminator='ThrottleByUserIdRule'):
        max_count: Optional[int]
        type: Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_USER_ID_RULE]

        @overload
        def __init__(
                self, 
                *, 
                max_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.TrackedResource(Resource):
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


    class azure.mgmt.signalr.models.TrafficThrottleByJwtCustomClaimRule(ClientTrafficControlRule, discriminator='TrafficThrottleByJwtCustomClaimRule'):
        aggregation_window_in_seconds: Optional[int]
        claim_name: str
        max_inbound_message_bytes: Optional[int]
        type: Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_window_in_seconds: Optional[int] = ..., 
                claim_name: str, 
                max_inbound_message_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.TrafficThrottleByJwtSignatureRule(ClientTrafficControlRule, discriminator='TrafficThrottleByJwtSignatureRule'):
        aggregation_window_in_seconds: Optional[int]
        max_inbound_message_bytes: Optional[int]
        type: Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_JWT_SIGNATURE_RULE]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_window_in_seconds: Optional[int] = ..., 
                max_inbound_message_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.TrafficThrottleByUserIdRule(ClientTrafficControlRule, discriminator='TrafficThrottleByUserIdRule'):
        aggregation_window_in_seconds: Optional[int]
        max_inbound_message_bytes: Optional[int]
        type: Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_USER_ID_RULE]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_window_in_seconds: Optional[int] = ..., 
                max_inbound_message_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.UpstreamAuthSettings(_Model):
        managed_identity: Optional[ManagedIdentitySettings]
        type: Optional[Union[str, UpstreamAuthType]]

        @overload
        def __init__(
                self, 
                *, 
                managed_identity: Optional[ManagedIdentitySettings] = ..., 
                type: Optional[Union[str, UpstreamAuthType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.UpstreamAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_IDENTITY = "ManagedIdentity"
        NONE = "None"


    class azure.mgmt.signalr.models.UpstreamTemplate(_Model):
        auth: Optional[UpstreamAuthSettings]
        category_pattern: Optional[str]
        event_pattern: Optional[str]
        hub_pattern: Optional[str]
        url_template: str

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[UpstreamAuthSettings] = ..., 
                category_pattern: Optional[str] = ..., 
                event_pattern: Optional[str] = ..., 
                hub_pattern: Optional[str] = ..., 
                url_template: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.signalr.models.UserAssignedIdentityProperty(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.signalr.operations

    class azure.mgmt.signalr.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.signalr.operations.SignalRCustomCertificatesOperations:

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
                certificate_name: str, 
                parameters: CustomCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomCertificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                parameters: CustomCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomCertificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomCertificate]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CustomCertificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CustomCertificate]: ...


    class azure.mgmt.signalr.operations.SignalRCustomDomainsOperations:

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
                name: str, 
                parameters: CustomDomain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomDomain]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                parameters: CustomDomain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomDomain]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomDomain]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                **kwargs: Any
            ) -> CustomDomain: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CustomDomain]: ...


    class azure.mgmt.signalr.operations.SignalROperations:

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
                parameters: SignalRResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalRResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: SignalRResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalRResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalRResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalRKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalRKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalRKeys]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: SignalRResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalRResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: SignalRResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalRResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalRResource]: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                parameters: NameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                parameters: NameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailability: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> SignalRResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SignalRResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SignalRResource]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> SignalRKeys: ...

        @distributed_trace
        def list_replica_skus(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> SkuList: ...

        @distributed_trace
        def list_skus(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> SkuList: ...


    class azure.mgmt.signalr.operations.SignalRPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                private_endpoint_connection_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                private_endpoint_connection_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...

        @overload
        def update(
                self, 
                private_endpoint_connection_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def update(
                self, 
                private_endpoint_connection_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def update(
                self, 
                private_endpoint_connection_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.signalr.operations.SignalRPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.signalr.operations.SignalRReplicaSharedPrivateLinkResourcesOperations:

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
                replica_name: str, 
                shared_private_link_resource_name: str, 
                parameters: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                shared_private_link_resource_name: str, 
                parameters: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                shared_private_link_resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                shared_private_link_resource_name: str, 
                **kwargs: Any
            ) -> SharedPrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SharedPrivateLinkResource]: ...


    class azure.mgmt.signalr.operations.SignalRReplicasOperations:

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
                replica_name: str, 
                parameters: Replica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replica]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                parameters: Replica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replica]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replica]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                parameters: Replica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replica]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                parameters: Replica, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replica]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replica]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                replica_name: str, 
                **kwargs: Any
            ) -> Replica: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Replica]: ...


    class azure.mgmt.signalr.operations.SignalRSharedPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                shared_private_link_resource_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                shared_private_link_resource_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                shared_private_link_resource_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                shared_private_link_resource_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                shared_private_link_resource_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> SharedPrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SharedPrivateLinkResource]: ...


    class azure.mgmt.signalr.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[SignalRUsage]: ...


namespace azure.mgmt.signalr.types

    class azure.mgmt.signalr.types.ApplicationFirewallSettings(TypedDict, total=False):
        key "maxClientConnectionLifetimeInSeconds": int
        clientConnectionCountRules: list[ClientConnectionCountRule]
        clientTrafficControlRules: list[ClientTrafficControlRule]
        client_connection_count_rules: list[ClientConnectionCountRule]
        client_traffic_control_rules: list[ClientTrafficControlRule]
        max_client_connection_lifetime_in_seconds: int


    class azure.mgmt.signalr.types.ClientConnectionCountRuleDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE = "ThrottleByJwtCustomClaimRule"
        THROTTLE_BY_JWT_SIGNATURE_RULE = "ThrottleByJwtSignatureRule"
        THROTTLE_BY_USER_ID_RULE = "ThrottleByUserIdRule"


    class azure.mgmt.signalr.types.ClientTrafficControlRuleDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRAFFIC_THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE = "TrafficThrottleByJwtCustomClaimRule"
        TRAFFIC_THROTTLE_BY_JWT_SIGNATURE_RULE = "TrafficThrottleByJwtSignatureRule"
        TRAFFIC_THROTTLE_BY_USER_ID_RULE = "TrafficThrottleByUserIdRule"


    class azure.mgmt.signalr.types.CustomCertificate(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[CustomCertificateProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CustomCertificateProperties
        system_data: SystemData
        type: str


    class azure.mgmt.signalr.types.CustomCertificateProperties(TypedDict, total=False):
        key "keyVaultBaseUri": Required[str]
        key "keyVaultSecretName": Required[str]
        key "keyVaultSecretVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        key_vault_base_uri: str
        key_vault_secret_name: str
        key_vault_secret_version: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.signalr.types.CustomDomain(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[CustomDomainProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CustomDomainProperties
        system_data: SystemData
        type: str


    class azure.mgmt.signalr.types.CustomDomainProperties(TypedDict, total=False):
        key "customCertificate": Required[ResourceReference]
        key "domainName": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        custom_certificate: ResourceReference
        domain_name: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.signalr.types.Dimension(TypedDict, total=False):
        key "displayName": str
        key "internalName": str
        key "name": str
        key "toBeExportedForShoebox": bool
        display_name: str
        internal_name: str
        name: str
        to_be_exported_for_shoebox: bool


    class azure.mgmt.signalr.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.signalr.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.signalr.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.signalr.types.IPRule(TypedDict, total=False):
        key "action": Union[str, ACLAction]
        key "value": str
        action: Union[str, ACLAction]
        value: str


    class azure.mgmt.signalr.types.LiveTraceCategory(TypedDict, total=False):
        key "enabled": str
        key "name": str
        enabled: str
        name: str


    class azure.mgmt.signalr.types.LiveTraceConfiguration(TypedDict, total=False):
        key "enabled": str
        categories: list[LiveTraceCategory]
        enabled: str


    class azure.mgmt.signalr.types.LogSpecification(TypedDict, total=False):
        key "displayName": str
        key "name": str
        display_name: str
        name: str


    class azure.mgmt.signalr.types.ManagedIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ManagedIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentityProperty]
        user_assigned_identities: dict[str, UserAssignedIdentityProperty]


    class azure.mgmt.signalr.types.ManagedIdentitySettings(TypedDict, total=False):
        key "resource": str
        resource: str


    class azure.mgmt.signalr.types.MetricSpecification(TypedDict, total=False):
        key "aggregationType": str
        key "category": str
        key "displayDescription": str
        key "displayName": str
        key "fillGapWithZero": str
        key "name": str
        key "unit": str
        aggregation_type: str
        category: str
        dimensions: list[Dimension]
        display_description: str
        display_name: str
        fill_gap_with_zero: str
        name: str
        unit: str


    class azure.mgmt.signalr.types.NameAvailability(TypedDict, total=False):
        key "message": str
        key "nameAvailable": bool
        key "reason": str
        message: str
        name_available: bool
        reason: str


    class azure.mgmt.signalr.types.NameAvailabilityParameters(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[str]
        name: str
        type: str


    class azure.mgmt.signalr.types.NetworkACL(TypedDict, total=False):
        allow: list[Union[str, SignalRRequestType]]
        deny: list[Union[str, SignalRRequestType]]


    class azure.mgmt.signalr.types.Operation(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": str
        key "properties": ForwardRef('OperationProperties', module='types')
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: str
        properties: OperationProperties


    class azure.mgmt.signalr.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.signalr.types.OperationProperties(TypedDict, total=False):
        key "serviceSpecification": ForwardRef('ServiceSpecification', module='types')
        service_specification: ServiceSpecification


    class azure.mgmt.signalr.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.signalr.types.PrivateEndpointACL(NetworkACL):
        key "name": Required[str]
        allow: list[Union[str, SignalRRequestType]]
        deny: list[Union[str, SignalRRequestType]]
        name: str


    class azure.mgmt.signalr.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.signalr.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionState', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.signalr.types.PrivateLinkResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateLinkResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.signalr.types.PrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        group_id: str
        requiredMembers: list[str]
        requiredZoneNames: list[str]
        required_members: list[str]
        required_zone_names: list[str]
        shareablePrivateLinkResourceTypes: list[ShareablePrivateLinkResourceType]
        shareable_private_link_resource_types: list[ShareablePrivateLinkResourceType]


    class azure.mgmt.signalr.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateLinkServiceConnectionStatus]
        actions_required: str
        description: str
        status: Union[str, PrivateLinkServiceConnectionStatus]


    class azure.mgmt.signalr.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.signalr.types.RegenerateKeyParameters(TypedDict, total=False):
        key "keyType": Union[str, KeyType]
        key_type: Union[str, KeyType]


    class azure.mgmt.signalr.types.Replica(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ReplicaProperties', module='types')
        key "sku": ForwardRef('ResourceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ReplicaProperties
        sku: ResourceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.signalr.types.ReplicaProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "regionEndpointEnabled": str
        key "resourceStopped": str
        provisioning_state: Union[str, ProvisioningState]
        region_endpoint_enabled: str
        resource_stopped: str


    class azure.mgmt.signalr.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.signalr.types.ResourceLogCategory(TypedDict, total=False):
        key "enabled": str
        key "name": str
        enabled: str
        name: str


    class azure.mgmt.signalr.types.ResourceLogConfiguration(TypedDict, total=False):
        categories: list[ResourceLogCategory]


    class azure.mgmt.signalr.types.ResourceReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.signalr.types.ResourceSku(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": Required[str]
        key "size": str
        key "tier": Union[str, SignalRSkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SignalRSkuTier]


    class azure.mgmt.signalr.types.RouteSettings(TypedDict, total=False):
        key "connectionBalanceWeight": int
        key "latencyWeight": int
        key "serverBalanceWeight": int
        connection_balance_weight: int
        latency_weight: int
        server_balance_weight: int


    class azure.mgmt.signalr.types.ServerlessSettings(TypedDict, total=False):
        key "connectionTimeoutInSeconds": int
        key "keepAliveIntervalInSeconds": int
        connection_timeout_in_seconds: int
        keep_alive_interval_in_seconds: int


    class azure.mgmt.signalr.types.ServerlessUpstreamSettings(TypedDict, total=False):
        templates: list[UpstreamTemplate]


    class azure.mgmt.signalr.types.ServiceSpecification(TypedDict, total=False):
        logSpecifications: list[LogSpecification]
        log_specifications: list[LogSpecification]
        metricSpecifications: list[MetricSpecification]
        metric_specifications: list[MetricSpecification]


    class azure.mgmt.signalr.types.ShareablePrivateLinkResourceProperties(TypedDict, total=False):
        key "description": str
        key "groupId": str
        key "type": str
        description: str
        group_id: str
        type: str


    class azure.mgmt.signalr.types.ShareablePrivateLinkResourceType(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('ShareablePrivateLinkResourceProperties', module='types')
        name: str
        properties: ShareablePrivateLinkResourceProperties


    class azure.mgmt.signalr.types.SharedPrivateLinkResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SharedPrivateLinkResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SharedPrivateLinkResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.signalr.types.SharedPrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": Required[str]
        key "privateLinkResourceId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "requestMessage": str
        key "status": Union[str, SharedPrivateLinkResourceStatus]
        fqdns: list[str]
        group_id: str
        private_link_resource_id: str
        provisioning_state: Union[str, ProvisioningState]
        request_message: str
        status: Union[str, SharedPrivateLinkResourceStatus]


    class azure.mgmt.signalr.types.SignalRCorsSettings(TypedDict, total=False):
        allowedOrigins: list[str]
        allowed_origins: list[str]


    class azure.mgmt.signalr.types.SignalRFeature(TypedDict, total=False):
        key "flag": Required[Union[str, FeatureFlags]]
        key "value": Required[str]
        flag: Union[str, FeatureFlags]
        properties: dict[str, str]
        value: str


    class azure.mgmt.signalr.types.SignalRKeys(TypedDict, total=False):
        key "primaryConnectionString": str
        key "primaryKey": str
        key "secondaryConnectionString": str
        key "secondaryKey": str
        primary_connection_string: str
        primary_key: str
        secondary_connection_string: str
        secondary_key: str


    class azure.mgmt.signalr.types.SignalRNetworkACLs(TypedDict, total=False):
        key "defaultAction": Union[str, ACLAction]
        key "publicNetwork": ForwardRef('NetworkACL', module='types')
        default_action: Union[str, ACLAction]
        ipRules: list[IPRule]
        ip_rules: list[IPRule]
        privateEndpoints: list[PrivateEndpointACL]
        private_endpoints: list[PrivateEndpointACL]
        public_network: NetworkACL


    class azure.mgmt.signalr.types.SignalRProperties(TypedDict, total=False):
        key "applicationFirewall": ForwardRef('ApplicationFirewallSettings', module='types')
        key "cors": ForwardRef('SignalRCorsSettings', module='types')
        key "disableAadAuth": bool
        key "disableLocalAuth": bool
        key "externalIP": str
        key "hostName": str
        key "hostNamePrefix": str
        key "liveTraceConfiguration": ForwardRef('LiveTraceConfiguration', module='types')
        key "networkACLs": ForwardRef('SignalRNetworkACLs', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": str
        key "publicPort": int
        key "regionEndpointEnabled": str
        key "resourceLogConfiguration": ForwardRef('ResourceLogConfiguration', module='types')
        key "resourceStopped": str
        key "routeSettings": ForwardRef('RouteSettings', module='types')
        key "serverPort": int
        key "serverless": ForwardRef('ServerlessSettings', module='types')
        key "tls": ForwardRef('SignalRTlsSettings', module='types')
        key "upstream": ForwardRef('ServerlessUpstreamSettings', module='types')
        key "version": str
        application_firewall: ApplicationFirewallSettings
        cors: SignalRCorsSettings
        disable_aad_auth: bool
        disable_local_auth: bool
        external_ip: str
        features: list[SignalRFeature]
        host_name: str
        host_name_prefix: str
        live_trace_configuration: LiveTraceConfiguration
        network_ac_ls: SignalRNetworkACLs
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: str
        public_port: int
        region_endpoint_enabled: str
        resource_log_configuration: ResourceLogConfiguration
        resource_stopped: str
        route_settings: RouteSettings
        server_port: int
        serverless: ServerlessSettings
        sharedPrivateLinkResources: list[SharedPrivateLinkResource]
        shared_private_link_resources: list[SharedPrivateLinkResource]
        tls: SignalRTlsSettings
        upstream: ServerlessUpstreamSettings
        version: str


    class azure.mgmt.signalr.types.SignalRResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "kind": Union[str, ServiceKind]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SignalRProperties', module='types')
        key "sku": ForwardRef('ResourceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedIdentity
        kind: Union[str, ServiceKind]
        location: str
        name: str
        properties: SignalRProperties
        sku: ResourceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.signalr.types.SignalRTlsSettings(TypedDict, total=False):
        key "clientCertEnabled": bool
        client_cert_enabled: bool


    class azure.mgmt.signalr.types.SignalRUsage(TypedDict, total=False):
        key "currentValue": int
        key "id": str
        key "limit": int
        key "name": ForwardRef('SignalRUsageName', module='types')
        key "unit": str
        current_value: int
        id: str
        limit: int
        name: SignalRUsageName
        unit: str


    class azure.mgmt.signalr.types.SignalRUsageName(TypedDict, total=False):
        key "localizedValue": str
        key "value": str
        localized_value: str
        value: str


    class azure.mgmt.signalr.types.Sku(TypedDict, total=False):
        key "capacity": ForwardRef('SkuCapacity', module='types')
        key "resourceType": str
        key "sku": ForwardRef('ResourceSku', module='types')
        capacity: SkuCapacity
        resource_type: str
        sku: ResourceSku


    class azure.mgmt.signalr.types.SkuCapacity(TypedDict, total=False):
        key "default": int
        key "maximum": int
        key "minimum": int
        key "scaleType": Union[str, ScaleType]
        allowedValues: list[int]
        allowed_values: list[int]
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, ScaleType]


    class azure.mgmt.signalr.types.SkuList(TypedDict, total=False):
        key "nextLink": str
        next_link: str
        value: list[Sku]


    class azure.mgmt.signalr.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.signalr.types.ThrottleByJwtCustomClaimRule(TypedDict, total=False):
        key "claimName": Required[str]
        key "maxCount": int
        key "type": Required[Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE]]
        claim_name: str
        max_count: int
        type: Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE]


    class azure.mgmt.signalr.types.ThrottleByJwtSignatureRule(TypedDict, total=False):
        key "maxCount": int
        key "type": Required[Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_JWT_SIGNATURE_RULE]]
        max_count: int
        type: Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_JWT_SIGNATURE_RULE]


    class azure.mgmt.signalr.types.ThrottleByUserIdRule(TypedDict, total=False):
        key "maxCount": int
        key "type": Required[Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_USER_ID_RULE]]
        max_count: int
        type: Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_USER_ID_RULE]


    class azure.mgmt.signalr.types.TrackedResource(Resource):
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


    class azure.mgmt.signalr.types.TrafficThrottleByJwtCustomClaimRule(TypedDict, total=False):
        key "aggregationWindowInSeconds": int
        key "claimName": Required[str]
        key "maxInboundMessageBytes": int
        key "type": Required[Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE]]
        aggregation_window_in_seconds: int
        claim_name: str
        max_inbound_message_bytes: int
        type: Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE]


    class azure.mgmt.signalr.types.TrafficThrottleByJwtSignatureRule(TypedDict, total=False):
        key "aggregationWindowInSeconds": int
        key "maxInboundMessageBytes": int
        key "type": Required[Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_JWT_SIGNATURE_RULE]]
        aggregation_window_in_seconds: int
        max_inbound_message_bytes: int
        type: Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_JWT_SIGNATURE_RULE]


    class azure.mgmt.signalr.types.TrafficThrottleByUserIdRule(TypedDict, total=False):
        key "aggregationWindowInSeconds": int
        key "maxInboundMessageBytes": int
        key "type": Required[Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_USER_ID_RULE]]
        aggregation_window_in_seconds: int
        max_inbound_message_bytes: int
        type: Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_USER_ID_RULE]


    class azure.mgmt.signalr.types.UpstreamAuthSettings(TypedDict, total=False):
        key "managedIdentity": ForwardRef('ManagedIdentitySettings', module='types')
        key "type": Union[str, UpstreamAuthType]
        managed_identity: ManagedIdentitySettings
        type: Union[str, UpstreamAuthType]


    class azure.mgmt.signalr.types.UpstreamTemplate(TypedDict, total=False):
        key "auth": ForwardRef('UpstreamAuthSettings', module='types')
        key "categoryPattern": str
        key "eventPattern": str
        key "hubPattern": str
        key "urlTemplate": Required[str]
        auth: UpstreamAuthSettings
        category_pattern: str
        event_pattern: str
        hub_pattern: str
        url_template: str


    class azure.mgmt.signalr.types.UserAssignedIdentityProperty(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


```