```py
namespace azure.mgmt.webpubsub

    class azure.mgmt.webpubsub.WebPubSubManagementClient: implements ContextManager 
        operations: Operations
        usages: UsagesOperations
        web_pub_sub: WebPubSubOperations
        web_pub_sub_custom_certificates: WebPubSubCustomCertificatesOperations
        web_pub_sub_custom_domains: WebPubSubCustomDomainsOperations
        web_pub_sub_hubs: WebPubSubHubsOperations
        web_pub_sub_persistent_storages: WebPubSubPersistentStoragesOperations
        web_pub_sub_private_endpoint_connections: WebPubSubPrivateEndpointConnectionsOperations
        web_pub_sub_private_link_resources: WebPubSubPrivateLinkResourcesOperations
        web_pub_sub_replica_shared_private_link_resources: WebPubSubReplicaSharedPrivateLinkResourcesOperations
        web_pub_sub_replicas: WebPubSubReplicasOperations
        web_pub_sub_shared_private_link_resources: WebPubSubSharedPrivateLinkResourcesOperations

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


namespace azure.mgmt.webpubsub.aio

    class azure.mgmt.webpubsub.aio.WebPubSubManagementClient: implements AsyncContextManager 
        operations: Operations
        usages: UsagesOperations
        web_pub_sub: WebPubSubOperations
        web_pub_sub_custom_certificates: WebPubSubCustomCertificatesOperations
        web_pub_sub_custom_domains: WebPubSubCustomDomainsOperations
        web_pub_sub_hubs: WebPubSubHubsOperations
        web_pub_sub_persistent_storages: WebPubSubPersistentStoragesOperations
        web_pub_sub_private_endpoint_connections: WebPubSubPrivateEndpointConnectionsOperations
        web_pub_sub_private_link_resources: WebPubSubPrivateLinkResourcesOperations
        web_pub_sub_replica_shared_private_link_resources: WebPubSubReplicaSharedPrivateLinkResourcesOperations
        web_pub_sub_replicas: WebPubSubReplicasOperations
        web_pub_sub_shared_private_link_resources: WebPubSubSharedPrivateLinkResourcesOperations

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


namespace azure.mgmt.webpubsub.aio.operations

    class azure.mgmt.webpubsub.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.webpubsub.aio.operations.UsagesOperations:

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
            ) -> AsyncItemPaged[SignalRServiceUsage]: ...


    class azure.mgmt.webpubsub.aio.operations.WebPubSubCustomCertificatesOperations:

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


    class azure.mgmt.webpubsub.aio.operations.WebPubSubCustomDomainsOperations:

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


    class azure.mgmt.webpubsub.aio.operations.WebPubSubHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                hub_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: WebPubSubHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubHub]: ...

        @overload
        async def begin_create_or_update(
                self, 
                hub_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: WebPubSubHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubHub]: ...

        @overload
        async def begin_create_or_update(
                self, 
                hub_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubHub]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                hub_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                hub_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> WebPubSubHub: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WebPubSubHub]: ...


    class azure.mgmt.webpubsub.aio.operations.WebPubSubOperations:

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
                parameters: WebPubSubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: WebPubSubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubResource]: ...

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
            ) -> AsyncLROPoller[WebPubSubKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubKeys]: ...

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
                parameters: WebPubSubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: WebPubSubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WebPubSubResource]: ...

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
            ) -> WebPubSubResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WebPubSubResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[WebPubSubResource]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> WebPubSubKeys: ...

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


    class azure.mgmt.webpubsub.aio.operations.WebPubSubPersistentStoragesOperations:

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
                parameters: PersistentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PersistentStorage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                parameters: PersistentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PersistentStorage]: ...

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
            ) -> AsyncLROPoller[PersistentStorage]: ...

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
            ) -> PersistentStorage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PersistentStorage]: ...


    class azure.mgmt.webpubsub.aio.operations.WebPubSubPrivateEndpointConnectionsOperations:

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


    class azure.mgmt.webpubsub.aio.operations.WebPubSubPrivateLinkResourcesOperations:

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


    class azure.mgmt.webpubsub.aio.operations.WebPubSubReplicaSharedPrivateLinkResourcesOperations:

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


    class azure.mgmt.webpubsub.aio.operations.WebPubSubReplicasOperations:

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


    class azure.mgmt.webpubsub.aio.operations.WebPubSubSharedPrivateLinkResourcesOperations:

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


namespace azure.mgmt.webpubsub.models

    class azure.mgmt.webpubsub.models.ACLAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.webpubsub.models.ApplicationFirewallSettings(_Model):
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


    class azure.mgmt.webpubsub.models.ChatSettings(_Model):
        mode: Optional[str]
        persistent_storage: Optional[ResourceReference]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[str] = ..., 
                persistent_storage: Optional[ResourceReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.ClientConnectionCountRule(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.ClientConnectionCountRuleDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE = "ThrottleByJwtCustomClaimRule"
        THROTTLE_BY_JWT_SIGNATURE_RULE = "ThrottleByJwtSignatureRule"
        THROTTLE_BY_USER_ID_RULE = "ThrottleByUserIdRule"


    class azure.mgmt.webpubsub.models.ClientTrafficControlRule(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.ClientTrafficControlRuleDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRAFFIC_THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE = "TrafficThrottleByJwtCustomClaimRule"
        TRAFFIC_THROTTLE_BY_JWT_SIGNATURE_RULE = "TrafficThrottleByJwtSignatureRule"
        TRAFFIC_THROTTLE_BY_USER_ID_RULE = "TrafficThrottleByUserIdRule"


    class azure.mgmt.webpubsub.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.webpubsub.models.CustomCertificate(ProxyResource):
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


    class azure.mgmt.webpubsub.models.CustomCertificateProperties(_Model):
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


    class azure.mgmt.webpubsub.models.CustomDomain(ProxyResource):
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


    class azure.mgmt.webpubsub.models.CustomDomainProperties(_Model):
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


    class azure.mgmt.webpubsub.models.Dimension(_Model):
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


    class azure.mgmt.webpubsub.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.webpubsub.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.webpubsub.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.EventHandler(_Model):
        auth: Optional[UpstreamAuthSettings]
        group_presence_events: Optional[GroupPresenceEventFilters]
        system_events: Optional[list[str]]
        url_template: str
        user_event_pattern: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[UpstreamAuthSettings] = ..., 
                group_presence_events: Optional[GroupPresenceEventFilters] = ..., 
                system_events: Optional[list[str]] = ..., 
                url_template: str, 
                user_event_pattern: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.EventHubEndpoint(EventListenerEndpoint, discriminator='EventHub'):
        event_hub_name: str
        fully_qualified_namespace: str
        type: Literal[EventListenerEndpointDiscriminator.EVENT_HUB]

        @overload
        def __init__(
                self, 
                *, 
                event_hub_name: str, 
                fully_qualified_namespace: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.EventListener(_Model):
        endpoint: EventListenerEndpoint
        filter: EventListenerFilter

        @overload
        def __init__(
                self, 
                *, 
                endpoint: EventListenerEndpoint, 
                filter: EventListenerFilter
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.EventListenerEndpoint(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.EventListenerEndpointDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_HUB = "EventHub"


    class azure.mgmt.webpubsub.models.EventListenerFilter(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.EventListenerFilterDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_NAME = "EventName"


    class azure.mgmt.webpubsub.models.EventNameFilter(EventListenerFilter, discriminator='EventName'):
        system_events: Optional[list[str]]
        type: Literal[EventListenerFilterDiscriminator.EVENT_NAME]
        user_event_pattern: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                system_events: Optional[list[str]] = ..., 
                user_event_pattern: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.GroupPresenceEventFilters(_Model):
        event_names: list[Union[str, GroupPresenceEventName]]
        group_filters: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                event_names: list[Union[str, GroupPresenceEventName]], 
                group_filters: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.GroupPresenceEventName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JOINED = "joined"
        LEFT = "left"


    class azure.mgmt.webpubsub.models.IPRule(_Model):
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


    class azure.mgmt.webpubsub.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SALT = "Salt"
        SECONDARY = "Secondary"


    class azure.mgmt.webpubsub.models.LiveTraceCategory(_Model):
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


    class azure.mgmt.webpubsub.models.LiveTraceConfiguration(_Model):
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


    class azure.mgmt.webpubsub.models.LogSpecification(_Model):
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


    class azure.mgmt.webpubsub.models.ManagedIdentity(_Model):
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


    class azure.mgmt.webpubsub.models.ManagedIdentitySettings(_Model):
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.ManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.webpubsub.models.MetricSpecification(_Model):
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


    class azure.mgmt.webpubsub.models.NameAvailability(_Model):
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


    class azure.mgmt.webpubsub.models.NameAvailabilityParameters(_Model):
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


    class azure.mgmt.webpubsub.models.NetworkACL(_Model):
        allow: Optional[list[Union[str, WebPubSubRequestType]]]
        deny: Optional[list[Union[str, WebPubSubRequestType]]]

        @overload
        def __init__(
                self, 
                *, 
                allow: Optional[list[Union[str, WebPubSubRequestType]]] = ..., 
                deny: Optional[list[Union[str, WebPubSubRequestType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.Operation(_Model):
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


    class azure.mgmt.webpubsub.models.OperationDisplay(_Model):
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


    class azure.mgmt.webpubsub.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.PersistentStorage(ProxyResource):
        id: str
        name: str
        properties: PersistentStorageProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: PersistentStorageProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.webpubsub.models.PersistentStorageProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        storage_account: ResourceReference

        @overload
        def __init__(
                self, 
                *, 
                storage_account: ResourceReference
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.PrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.PrivateEndpointACL(NetworkACL):
        allow: Union[list[str, WebPubSubRequestType]]
        deny: Union[list[str, WebPubSubRequestType]]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                allow: Optional[list[Union[str, WebPubSubRequestType]]] = ..., 
                deny: Optional[list[Union[str, WebPubSubRequestType]]] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.webpubsub.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.webpubsub.models.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.webpubsub.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.webpubsub.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.webpubsub.models.PrivateLinkServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.webpubsub.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.webpubsub.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.webpubsub.models.RegenerateKeyParameters(_Model):
        key_type: Optional[Union[str, KeyType]]

        @overload
        def __init__(
                self, 
                *, 
                key_type: Optional[Union[str, KeyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.Replica(TrackedResource):
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


    class azure.mgmt.webpubsub.models.ReplicaProperties(_Model):
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


    class azure.mgmt.webpubsub.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.webpubsub.models.ResourceLogCategory(_Model):
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


    class azure.mgmt.webpubsub.models.ResourceLogConfiguration(_Model):
        categories: Optional[list[ResourceLogCategory]]

        @overload
        def __init__(
                self, 
                *, 
                categories: Optional[list[ResourceLogCategory]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.ResourceReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.ResourceSku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[Union[str, WebPubSubSkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: str, 
                tier: Optional[Union[str, WebPubSubSkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.ScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.webpubsub.models.ServiceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SOCKET_IO = "SocketIO"
        WEB_PUB_SUB = "WebPubSub"


    class azure.mgmt.webpubsub.models.ServiceSpecification(_Model):
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


    class azure.mgmt.webpubsub.models.ShareablePrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.webpubsub.models.ShareablePrivateLinkResourceType(_Model):
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


    class azure.mgmt.webpubsub.models.SharedPrivateLinkResource(ProxyResource):
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


    class azure.mgmt.webpubsub.models.SharedPrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.webpubsub.models.SharedPrivateLinkResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"
        TIMEOUT = "Timeout"


    class azure.mgmt.webpubsub.models.SignalRServiceUsage(_Model):
        current_value: Optional[int]
        id: Optional[str]
        limit: Optional[int]
        name: Optional[SignalRServiceUsageName]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[SignalRServiceUsageName] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.SignalRServiceUsageName(_Model):
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


    class azure.mgmt.webpubsub.models.Sku(_Model):
        capacity: Optional[SkuCapacity]
        resource_type: Optional[str]
        sku: Optional[ResourceSku]


    class azure.mgmt.webpubsub.models.SkuCapacity(_Model):
        allowed_values: Optional[list[int]]
        default: Optional[int]
        maximum: Optional[int]
        minimum: Optional[int]
        scale_type: Optional[Union[str, ScaleType]]


    class azure.mgmt.webpubsub.models.SkuList(_Model):
        next_link: Optional[str]
        value: Optional[list[Sku]]


    class azure.mgmt.webpubsub.models.SystemData(_Model):
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


    class azure.mgmt.webpubsub.models.ThrottleByJwtCustomClaimRule(ClientConnectionCountRule, discriminator='ThrottleByJwtCustomClaimRule'):
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


    class azure.mgmt.webpubsub.models.ThrottleByJwtSignatureRule(ClientConnectionCountRule, discriminator='ThrottleByJwtSignatureRule'):
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


    class azure.mgmt.webpubsub.models.ThrottleByUserIdRule(ClientConnectionCountRule, discriminator='ThrottleByUserIdRule'):
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


    class azure.mgmt.webpubsub.models.TrackedResource(Resource):
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


    class azure.mgmt.webpubsub.models.TrafficThrottleByJwtCustomClaimRule(ClientTrafficControlRule, discriminator='TrafficThrottleByJwtCustomClaimRule'):
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


    class azure.mgmt.webpubsub.models.TrafficThrottleByJwtSignatureRule(ClientTrafficControlRule, discriminator='TrafficThrottleByJwtSignatureRule'):
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


    class azure.mgmt.webpubsub.models.TrafficThrottleByUserIdRule(ClientTrafficControlRule, discriminator='TrafficThrottleByUserIdRule'):
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


    class azure.mgmt.webpubsub.models.UpstreamAuthSettings(_Model):
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


    class azure.mgmt.webpubsub.models.UpstreamAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_IDENTITY = "ManagedIdentity"
        NONE = "None"


    class azure.mgmt.webpubsub.models.UserAssignedIdentityProperty(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.webpubsub.models.WebPubSubHub(ProxyResource):
        id: str
        name: str
        properties: WebPubSubHubProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: WebPubSubHubProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.WebPubSubHubProperties(_Model):
        anonymous_connect_policy: Optional[str]
        chat: Optional[ChatSettings]
        event_handlers: Optional[list[EventHandler]]
        event_listeners: Optional[list[EventListener]]
        web_socket_keep_alive_interval_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                anonymous_connect_policy: Optional[str] = ..., 
                chat: Optional[ChatSettings] = ..., 
                event_handlers: Optional[list[EventHandler]] = ..., 
                event_listeners: Optional[list[EventListener]] = ..., 
                web_socket_keep_alive_interval_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.WebPubSubKeys(_Model):
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


    class azure.mgmt.webpubsub.models.WebPubSubNetworkACLs(_Model):
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


    class azure.mgmt.webpubsub.models.WebPubSubProperties(_Model):
        application_firewall: Optional[ApplicationFirewallSettings]
        disable_aad_auth: Optional[bool]
        disable_local_auth: Optional[bool]
        external_ip: Optional[str]
        host_name: Optional[str]
        host_name_prefix: Optional[str]
        live_trace_configuration: Optional[LiveTraceConfiguration]
        network_ac_ls: Optional[WebPubSubNetworkACLs]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[str]
        public_port: Optional[int]
        region_endpoint_enabled: Optional[str]
        resource_log_configuration: Optional[ResourceLogConfiguration]
        resource_stopped: Optional[str]
        server_port: Optional[int]
        shared_private_link_resources: Optional[list[SharedPrivateLinkResource]]
        socket_io: Optional[WebPubSubSocketIOSettings]
        tls: Optional[WebPubSubTlsSettings]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_firewall: Optional[ApplicationFirewallSettings] = ..., 
                disable_aad_auth: Optional[bool] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                live_trace_configuration: Optional[LiveTraceConfiguration] = ..., 
                network_ac_ls: Optional[WebPubSubNetworkACLs] = ..., 
                public_network_access: Optional[str] = ..., 
                region_endpoint_enabled: Optional[str] = ..., 
                resource_log_configuration: Optional[ResourceLogConfiguration] = ..., 
                resource_stopped: Optional[str] = ..., 
                socket_io: Optional[WebPubSubSocketIOSettings] = ..., 
                tls: Optional[WebPubSubTlsSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.WebPubSubRequestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_CONNECTION = "ClientConnection"
        RESTAPI = "RESTAPI"
        SERVER_CONNECTION = "ServerConnection"
        TRACE = "Trace"


    class azure.mgmt.webpubsub.models.WebPubSubResource(TrackedResource):
        id: str
        identity: Optional[ManagedIdentity]
        kind: Optional[Union[str, ServiceKind]]
        location: str
        name: str
        properties: Optional[WebPubSubProperties]
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
                properties: Optional[WebPubSubProperties] = ..., 
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


    class azure.mgmt.webpubsub.models.WebPubSubSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.webpubsub.models.WebPubSubSocketIOSettings(_Model):
        service_mode: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_mode: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.webpubsub.models.WebPubSubTlsSettings(_Model):
        client_cert_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                client_cert_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.webpubsub.operations

    class azure.mgmt.webpubsub.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.webpubsub.operations.UsagesOperations:

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
            ) -> ItemPaged[SignalRServiceUsage]: ...


    class azure.mgmt.webpubsub.operations.WebPubSubCustomCertificatesOperations:

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


    class azure.mgmt.webpubsub.operations.WebPubSubCustomDomainsOperations:

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


    class azure.mgmt.webpubsub.operations.WebPubSubHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                hub_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: WebPubSubHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubHub]: ...

        @overload
        def begin_create_or_update(
                self, 
                hub_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: WebPubSubHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubHub]: ...

        @overload
        def begin_create_or_update(
                self, 
                hub_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubHub]: ...

        @distributed_trace
        def begin_delete(
                self, 
                hub_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                hub_name: str, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> WebPubSubHub: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WebPubSubHub]: ...


    class azure.mgmt.webpubsub.operations.WebPubSubOperations:

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
                parameters: WebPubSubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: WebPubSubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubResource]: ...

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
            ) -> LROPoller[WebPubSubKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubKeys]: ...

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
                parameters: WebPubSubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: WebPubSubResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WebPubSubResource]: ...

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
            ) -> WebPubSubResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WebPubSubResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[WebPubSubResource]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> WebPubSubKeys: ...

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


    class azure.mgmt.webpubsub.operations.WebPubSubPersistentStoragesOperations:

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
                parameters: PersistentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PersistentStorage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                parameters: PersistentStorage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PersistentStorage]: ...

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
            ) -> LROPoller[PersistentStorage]: ...

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
            ) -> PersistentStorage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PersistentStorage]: ...


    class azure.mgmt.webpubsub.operations.WebPubSubPrivateEndpointConnectionsOperations:

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


    class azure.mgmt.webpubsub.operations.WebPubSubPrivateLinkResourcesOperations:

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


    class azure.mgmt.webpubsub.operations.WebPubSubReplicaSharedPrivateLinkResourcesOperations:

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


    class azure.mgmt.webpubsub.operations.WebPubSubReplicasOperations:

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


    class azure.mgmt.webpubsub.operations.WebPubSubSharedPrivateLinkResourcesOperations:

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


namespace azure.mgmt.webpubsub.types

    class azure.mgmt.webpubsub.types.ApplicationFirewallSettings(TypedDict, total=False):
        key "maxClientConnectionLifetimeInSeconds": int
        clientConnectionCountRules: list[ClientConnectionCountRule]
        clientTrafficControlRules: list[ClientTrafficControlRule]
        client_connection_count_rules: list[ClientConnectionCountRule]
        client_traffic_control_rules: list[ClientTrafficControlRule]
        max_client_connection_lifetime_in_seconds: int


    class azure.mgmt.webpubsub.types.ChatSettings(TypedDict, total=False):
        key "mode": str
        key "persistentStorage": ForwardRef('ResourceReference', module='types')
        mode: str
        persistent_storage: ResourceReference


    class azure.mgmt.webpubsub.types.ClientConnectionCountRuleDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE = "ThrottleByJwtCustomClaimRule"
        THROTTLE_BY_JWT_SIGNATURE_RULE = "ThrottleByJwtSignatureRule"
        THROTTLE_BY_USER_ID_RULE = "ThrottleByUserIdRule"


    class azure.mgmt.webpubsub.types.ClientTrafficControlRuleDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRAFFIC_THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE = "TrafficThrottleByJwtCustomClaimRule"
        TRAFFIC_THROTTLE_BY_JWT_SIGNATURE_RULE = "TrafficThrottleByJwtSignatureRule"
        TRAFFIC_THROTTLE_BY_USER_ID_RULE = "TrafficThrottleByUserIdRule"


    class azure.mgmt.webpubsub.types.CustomCertificate(ProxyResource):
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


    class azure.mgmt.webpubsub.types.CustomCertificateProperties(TypedDict, total=False):
        key "keyVaultBaseUri": Required[str]
        key "keyVaultSecretName": Required[str]
        key "keyVaultSecretVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        key_vault_base_uri: str
        key_vault_secret_name: str
        key_vault_secret_version: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.webpubsub.types.CustomDomain(ProxyResource):
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


    class azure.mgmt.webpubsub.types.CustomDomainProperties(TypedDict, total=False):
        key "customCertificate": Required[ResourceReference]
        key "domainName": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        custom_certificate: ResourceReference
        domain_name: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.webpubsub.types.Dimension(TypedDict, total=False):
        key "displayName": str
        key "internalName": str
        key "name": str
        key "toBeExportedForShoebox": bool
        display_name: str
        internal_name: str
        name: str
        to_be_exported_for_shoebox: bool


    class azure.mgmt.webpubsub.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.webpubsub.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.webpubsub.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.webpubsub.types.EventHandler(TypedDict, total=False):
        key "auth": ForwardRef('UpstreamAuthSettings', module='types')
        key "groupPresenceEvents": ForwardRef('GroupPresenceEventFilters', module='types')
        key "urlTemplate": Required[str]
        key "userEventPattern": str
        auth: UpstreamAuthSettings
        group_presence_events: GroupPresenceEventFilters
        systemEvents: list[str]
        system_events: list[str]
        url_template: str
        user_event_pattern: str


    class azure.mgmt.webpubsub.types.EventHubEndpoint(TypedDict, total=False):
        key "eventHubName": Required[str]
        key "fullyQualifiedNamespace": Required[str]
        key "type": Required[Literal[EventListenerEndpointDiscriminator.EVENT_HUB]]
        event_hub_name: str
        fully_qualified_namespace: str
        type: Literal[EventListenerEndpointDiscriminator.EVENT_HUB]


    class azure.mgmt.webpubsub.types.EventListener(TypedDict, total=False):
        key "endpoint": Required[EventListenerEndpoint]
        key "filter": Required[EventListenerFilter]
        endpoint: EventListenerEndpoint
        filter: EventListenerFilter


    class azure.mgmt.webpubsub.types.EventListenerEndpoint(TypedDict, total=False):
        key "eventHubName": Required[str]
        key "fullyQualifiedNamespace": Required[str]
        key "type": Required[Literal[EventListenerEndpointDiscriminator.EVENT_HUB]]
        event_hub_name: str
        fully_qualified_namespace: str
        type: Literal[EventListenerEndpointDiscriminator.EVENT_HUB]


    class azure.mgmt.webpubsub.types.EventListenerEndpointDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_HUB = "EventHub"


    class azure.mgmt.webpubsub.types.EventListenerFilter(TypedDict, total=False):
        key "type": Required[Literal[EventListenerFilterDiscriminator.EVENT_NAME]]
        key "userEventPattern": str
        systemEvents: list[str]
        system_events: list[str]
        type: Literal[EventListenerFilterDiscriminator.EVENT_NAME]
        user_event_pattern: str


    class azure.mgmt.webpubsub.types.EventListenerFilterDiscriminator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_NAME = "EventName"


    class azure.mgmt.webpubsub.types.EventNameFilter(TypedDict, total=False):
        key "type": Required[Literal[EventListenerFilterDiscriminator.EVENT_NAME]]
        key "userEventPattern": str
        systemEvents: list[str]
        system_events: list[str]
        type: Literal[EventListenerFilterDiscriminator.EVENT_NAME]
        user_event_pattern: str


    class azure.mgmt.webpubsub.types.GroupPresenceEventFilters(TypedDict, total=False):
        key "eventNames": Required[list[Union[str, GroupPresenceEventName]]]
        event_names: list[Union[str, GroupPresenceEventName]]
        groupFilters: list[str]
        group_filters: list[str]


    class azure.mgmt.webpubsub.types.IPRule(TypedDict, total=False):
        key "action": Union[str, ACLAction]
        key "value": str
        action: Union[str, ACLAction]
        value: str


    class azure.mgmt.webpubsub.types.LiveTraceCategory(TypedDict, total=False):
        key "enabled": str
        key "name": str
        enabled: str
        name: str


    class azure.mgmt.webpubsub.types.LiveTraceConfiguration(TypedDict, total=False):
        key "enabled": str
        categories: list[LiveTraceCategory]
        enabled: str


    class azure.mgmt.webpubsub.types.LogSpecification(TypedDict, total=False):
        key "displayName": str
        key "name": str
        display_name: str
        name: str


    class azure.mgmt.webpubsub.types.ManagedIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ManagedIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentityProperty]
        user_assigned_identities: dict[str, UserAssignedIdentityProperty]


    class azure.mgmt.webpubsub.types.ManagedIdentitySettings(TypedDict, total=False):
        key "resource": str
        resource: str


    class azure.mgmt.webpubsub.types.MetricSpecification(TypedDict, total=False):
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


    class azure.mgmt.webpubsub.types.NameAvailability(TypedDict, total=False):
        key "message": str
        key "nameAvailable": bool
        key "reason": str
        message: str
        name_available: bool
        reason: str


    class azure.mgmt.webpubsub.types.NameAvailabilityParameters(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[str]
        name: str
        type: str


    class azure.mgmt.webpubsub.types.NetworkACL(TypedDict, total=False):
        allow: list[Union[str, WebPubSubRequestType]]
        deny: list[Union[str, WebPubSubRequestType]]


    class azure.mgmt.webpubsub.types.Operation(TypedDict, total=False):
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


    class azure.mgmt.webpubsub.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.webpubsub.types.OperationProperties(TypedDict, total=False):
        key "serviceSpecification": ForwardRef('ServiceSpecification', module='types')
        service_specification: ServiceSpecification


    class azure.mgmt.webpubsub.types.PersistentStorage(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[PersistentStorageProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PersistentStorageProperties
        system_data: SystemData
        type: str


    class azure.mgmt.webpubsub.types.PersistentStorageProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "storageAccount": Required[ResourceReference]
        provisioning_state: Union[str, ProvisioningState]
        storage_account: ResourceReference


    class azure.mgmt.webpubsub.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.webpubsub.types.PrivateEndpointACL(NetworkACL):
        key "name": Required[str]
        allow: list[Union[str, WebPubSubRequestType]]
        deny: list[Union[str, WebPubSubRequestType]]
        name: str


    class azure.mgmt.webpubsub.types.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.webpubsub.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionState', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.webpubsub.types.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.webpubsub.types.PrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        group_id: str
        requiredMembers: list[str]
        requiredZoneNames: list[str]
        required_members: list[str]
        required_zone_names: list[str]
        shareablePrivateLinkResourceTypes: list[ShareablePrivateLinkResourceType]
        shareable_private_link_resource_types: list[ShareablePrivateLinkResourceType]


    class azure.mgmt.webpubsub.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateLinkServiceConnectionStatus]
        actions_required: str
        description: str
        status: Union[str, PrivateLinkServiceConnectionStatus]


    class azure.mgmt.webpubsub.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.webpubsub.types.RegenerateKeyParameters(TypedDict, total=False):
        key "keyType": Union[str, KeyType]
        key_type: Union[str, KeyType]


    class azure.mgmt.webpubsub.types.Replica(TrackedResource):
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


    class azure.mgmt.webpubsub.types.ReplicaProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "regionEndpointEnabled": str
        key "resourceStopped": str
        provisioning_state: Union[str, ProvisioningState]
        region_endpoint_enabled: str
        resource_stopped: str


    class azure.mgmt.webpubsub.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.webpubsub.types.ResourceLogCategory(TypedDict, total=False):
        key "enabled": str
        key "name": str
        enabled: str
        name: str


    class azure.mgmt.webpubsub.types.ResourceLogConfiguration(TypedDict, total=False):
        categories: list[ResourceLogCategory]


    class azure.mgmt.webpubsub.types.ResourceReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.webpubsub.types.ResourceSku(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": Required[str]
        key "size": str
        key "tier": Union[str, WebPubSubSkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, WebPubSubSkuTier]


    class azure.mgmt.webpubsub.types.ServiceSpecification(TypedDict, total=False):
        logSpecifications: list[LogSpecification]
        log_specifications: list[LogSpecification]
        metricSpecifications: list[MetricSpecification]
        metric_specifications: list[MetricSpecification]


    class azure.mgmt.webpubsub.types.ShareablePrivateLinkResourceProperties(TypedDict, total=False):
        key "description": str
        key "groupId": str
        key "type": str
        description: str
        group_id: str
        type: str


    class azure.mgmt.webpubsub.types.ShareablePrivateLinkResourceType(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('ShareablePrivateLinkResourceProperties', module='types')
        name: str
        properties: ShareablePrivateLinkResourceProperties


    class azure.mgmt.webpubsub.types.SharedPrivateLinkResource(ProxyResource):
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


    class azure.mgmt.webpubsub.types.SharedPrivateLinkResourceProperties(TypedDict, total=False):
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


    class azure.mgmt.webpubsub.types.SignalRServiceUsage(TypedDict, total=False):
        key "currentValue": int
        key "id": str
        key "limit": int
        key "name": ForwardRef('SignalRServiceUsageName', module='types')
        key "unit": str
        current_value: int
        id: str
        limit: int
        name: SignalRServiceUsageName
        unit: str


    class azure.mgmt.webpubsub.types.SignalRServiceUsageName(TypedDict, total=False):
        key "localizedValue": str
        key "value": str
        localized_value: str
        value: str


    class azure.mgmt.webpubsub.types.Sku(TypedDict, total=False):
        key "capacity": ForwardRef('SkuCapacity', module='types')
        key "resourceType": str
        key "sku": ForwardRef('ResourceSku', module='types')
        capacity: SkuCapacity
        resource_type: str
        sku: ResourceSku


    class azure.mgmt.webpubsub.types.SkuCapacity(TypedDict, total=False):
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


    class azure.mgmt.webpubsub.types.SkuList(TypedDict, total=False):
        key "nextLink": str
        next_link: str
        value: list[Sku]


    class azure.mgmt.webpubsub.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.webpubsub.types.ThrottleByJwtCustomClaimRule(TypedDict, total=False):
        key "claimName": Required[str]
        key "maxCount": int
        key "type": Required[Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE]]
        claim_name: str
        max_count: int
        type: Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE]


    class azure.mgmt.webpubsub.types.ThrottleByJwtSignatureRule(TypedDict, total=False):
        key "maxCount": int
        key "type": Required[Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_JWT_SIGNATURE_RULE]]
        max_count: int
        type: Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_JWT_SIGNATURE_RULE]


    class azure.mgmt.webpubsub.types.ThrottleByUserIdRule(TypedDict, total=False):
        key "maxCount": int
        key "type": Required[Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_USER_ID_RULE]]
        max_count: int
        type: Literal[ClientConnectionCountRuleDiscriminator.THROTTLE_BY_USER_ID_RULE]


    class azure.mgmt.webpubsub.types.TrackedResource(Resource):
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


    class azure.mgmt.webpubsub.types.TrafficThrottleByJwtCustomClaimRule(TypedDict, total=False):
        key "aggregationWindowInSeconds": int
        key "claimName": Required[str]
        key "maxInboundMessageBytes": int
        key "type": Required[Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE]]
        aggregation_window_in_seconds: int
        claim_name: str
        max_inbound_message_bytes: int
        type: Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_JWT_CUSTOM_CLAIM_RULE]


    class azure.mgmt.webpubsub.types.TrafficThrottleByJwtSignatureRule(TypedDict, total=False):
        key "aggregationWindowInSeconds": int
        key "maxInboundMessageBytes": int
        key "type": Required[Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_JWT_SIGNATURE_RULE]]
        aggregation_window_in_seconds: int
        max_inbound_message_bytes: int
        type: Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_JWT_SIGNATURE_RULE]


    class azure.mgmt.webpubsub.types.TrafficThrottleByUserIdRule(TypedDict, total=False):
        key "aggregationWindowInSeconds": int
        key "maxInboundMessageBytes": int
        key "type": Required[Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_USER_ID_RULE]]
        aggregation_window_in_seconds: int
        max_inbound_message_bytes: int
        type: Literal[ClientTrafficControlRuleDiscriminator.TRAFFIC_THROTTLE_BY_USER_ID_RULE]


    class azure.mgmt.webpubsub.types.UpstreamAuthSettings(TypedDict, total=False):
        key "managedIdentity": ForwardRef('ManagedIdentitySettings', module='types')
        key "type": Union[str, UpstreamAuthType]
        managed_identity: ManagedIdentitySettings
        type: Union[str, UpstreamAuthType]


    class azure.mgmt.webpubsub.types.UserAssignedIdentityProperty(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.webpubsub.types.WebPubSubHub(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[WebPubSubHubProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: WebPubSubHubProperties
        system_data: SystemData
        type: str


    class azure.mgmt.webpubsub.types.WebPubSubHubProperties(TypedDict, total=False):
        key "anonymousConnectPolicy": str
        key "chat": ForwardRef('ChatSettings', module='types')
        key "webSocketKeepAliveIntervalInSeconds": int
        anonymous_connect_policy: str
        chat: ChatSettings
        eventHandlers: list[EventHandler]
        eventListeners: list[EventListener]
        event_handlers: list[EventHandler]
        event_listeners: list[EventListener]
        web_socket_keep_alive_interval_in_seconds: int


    class azure.mgmt.webpubsub.types.WebPubSubKeys(TypedDict, total=False):
        key "primaryConnectionString": str
        key "primaryKey": str
        key "secondaryConnectionString": str
        key "secondaryKey": str
        primary_connection_string: str
        primary_key: str
        secondary_connection_string: str
        secondary_key: str


    class azure.mgmt.webpubsub.types.WebPubSubNetworkACLs(TypedDict, total=False):
        key "defaultAction": Union[str, ACLAction]
        key "publicNetwork": ForwardRef('NetworkACL', module='types')
        default_action: Union[str, ACLAction]
        ipRules: list[IPRule]
        ip_rules: list[IPRule]
        privateEndpoints: list[PrivateEndpointACL]
        private_endpoints: list[PrivateEndpointACL]
        public_network: NetworkACL


    class azure.mgmt.webpubsub.types.WebPubSubProperties(TypedDict, total=False):
        key "applicationFirewall": ForwardRef('ApplicationFirewallSettings', module='types')
        key "disableAadAuth": bool
        key "disableLocalAuth": bool
        key "externalIP": str
        key "hostName": str
        key "hostNamePrefix": str
        key "liveTraceConfiguration": ForwardRef('LiveTraceConfiguration', module='types')
        key "networkACLs": ForwardRef('WebPubSubNetworkACLs', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": str
        key "publicPort": int
        key "regionEndpointEnabled": str
        key "resourceLogConfiguration": ForwardRef('ResourceLogConfiguration', module='types')
        key "resourceStopped": str
        key "serverPort": int
        key "socketIO": ForwardRef('WebPubSubSocketIOSettings', module='types')
        key "tls": ForwardRef('WebPubSubTlsSettings', module='types')
        key "version": str
        application_firewall: ApplicationFirewallSettings
        disable_aad_auth: bool
        disable_local_auth: bool
        external_ip: str
        host_name: str
        host_name_prefix: str
        live_trace_configuration: LiveTraceConfiguration
        network_ac_ls: WebPubSubNetworkACLs
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: str
        public_port: int
        region_endpoint_enabled: str
        resource_log_configuration: ResourceLogConfiguration
        resource_stopped: str
        server_port: int
        sharedPrivateLinkResources: list[SharedPrivateLinkResource]
        shared_private_link_resources: list[SharedPrivateLinkResource]
        socket_io: WebPubSubSocketIOSettings
        tls: WebPubSubTlsSettings
        version: str


    class azure.mgmt.webpubsub.types.WebPubSubResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "kind": Union[str, ServiceKind]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('WebPubSubProperties', module='types')
        key "sku": ForwardRef('ResourceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedIdentity
        kind: Union[str, ServiceKind]
        location: str
        name: str
        properties: WebPubSubProperties
        sku: ResourceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.webpubsub.types.WebPubSubSocketIOSettings(TypedDict, total=False):
        key "serviceMode": str
        service_mode: str


    class azure.mgmt.webpubsub.types.WebPubSubTlsSettings(TypedDict, total=False):
        key "clientCertEnabled": bool
        client_cert_enabled: bool


```