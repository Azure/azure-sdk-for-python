```py
namespace azure.mgmt.eventgrid

    class azure.mgmt.eventgrid.EventGridManagementClient: implements ContextManager 
        ca_certificates: CaCertificatesOperations
        channels: ChannelsOperations
        client_groups: ClientGroupsOperations
        clients: ClientsOperations
        domain_event_subscriptions: DomainEventSubscriptionsOperations
        domain_topic_event_subscriptions: DomainTopicEventSubscriptionsOperations
        domain_topics: DomainTopicsOperations
        domains: DomainsOperations
        event_subscriptions: EventSubscriptionsOperations
        extension_topics: ExtensionTopicsOperations
        namespace_topic_event_subscriptions: NamespaceTopicEventSubscriptionsOperations
        namespace_topics: NamespaceTopicsOperations
        namespaces: NamespacesOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        partner_configurations: PartnerConfigurationsOperations
        partner_destinations: PartnerDestinationsOperations
        partner_namespaces: PartnerNamespacesOperations
        partner_registrations: PartnerRegistrationsOperations
        partner_topic_event_subscriptions: PartnerTopicEventSubscriptionsOperations
        partner_topics: PartnerTopicsOperations
        permission_bindings: PermissionBindingsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        system_topic_event_subscriptions: SystemTopicEventSubscriptionsOperations
        system_topics: SystemTopicsOperations
        topic_event_subscriptions: TopicEventSubscriptionsOperations
        topic_spaces: TopicSpacesOperations
        topic_types: TopicTypesOperations
        topics: TopicsOperations
        verified_partners: VerifiedPartnersOperations

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


namespace azure.mgmt.eventgrid.aio

    class azure.mgmt.eventgrid.aio.EventGridManagementClient: implements AsyncContextManager 
        ca_certificates: CaCertificatesOperations
        channels: ChannelsOperations
        client_groups: ClientGroupsOperations
        clients: ClientsOperations
        domain_event_subscriptions: DomainEventSubscriptionsOperations
        domain_topic_event_subscriptions: DomainTopicEventSubscriptionsOperations
        domain_topics: DomainTopicsOperations
        domains: DomainsOperations
        event_subscriptions: EventSubscriptionsOperations
        extension_topics: ExtensionTopicsOperations
        namespace_topic_event_subscriptions: NamespaceTopicEventSubscriptionsOperations
        namespace_topics: NamespaceTopicsOperations
        namespaces: NamespacesOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        partner_configurations: PartnerConfigurationsOperations
        partner_destinations: PartnerDestinationsOperations
        partner_namespaces: PartnerNamespacesOperations
        partner_registrations: PartnerRegistrationsOperations
        partner_topic_event_subscriptions: PartnerTopicEventSubscriptionsOperations
        partner_topics: PartnerTopicsOperations
        permission_bindings: PermissionBindingsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        system_topic_event_subscriptions: SystemTopicEventSubscriptionsOperations
        system_topics: SystemTopicsOperations
        topic_event_subscriptions: TopicEventSubscriptionsOperations
        topic_spaces: TopicSpacesOperations
        topic_types: TopicTypesOperations
        topics: TopicsOperations
        verified_partners: VerifiedPartnersOperations

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


namespace azure.mgmt.eventgrid.aio.operations

    class azure.mgmt.eventgrid.aio.operations.CaCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                ca_certificate_info: CaCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CaCertificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                ca_certificate_info: CaCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CaCertificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                ca_certificate_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CaCertificate]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                **kwargs: Any
            ) -> CaCertificate: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CaCertificate]: ...


    class azure.mgmt.eventgrid.aio.operations.ChannelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_info: Channel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Channel: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_info: Channel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Channel: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Channel: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> Channel: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_partner_namespace(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Channel]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_update_parameters: ChannelUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_update_parameters: ChannelUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.aio.operations.ClientGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                client_group_info: ClientGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClientGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                client_group_info: ClientGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClientGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                client_group_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClientGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                **kwargs: Any
            ) -> ClientGroup: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ClientGroup]: ...


    class azure.mgmt.eventgrid.aio.operations.ClientsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                client_info: Client, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Client]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                client_info: Client, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Client]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                client_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Client]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                **kwargs: Any
            ) -> Client: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Client]: ...


    class azure.mgmt.eventgrid.aio.operations.DomainEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.DomainTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.DomainTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainTopic]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> DomainTopic: ...

        @distributed_trace
        def list_by_domain(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DomainTopic]: ...


    class azure.mgmt.eventgrid.aio.operations.DomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_info: Domain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_info: Domain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_update_parameters: DomainUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_update_parameters: DomainUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> Domain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Domain]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Domain]: ...

        @distributed_trace_async
        async def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                regenerate_key_request: DomainRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                regenerate_key_request: DomainRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...


    class azure.mgmt.eventgrid.aio.operations.EventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_domain_topic(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                provider_namespace: str, 
                resource_type_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_resource_group_for_topic_type(
                self, 
                resource_group_name: str, 
                topic_type_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_subscription_for_topic_type(
                self, 
                topic_type_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_resource_group_for_topic_type(
                self, 
                resource_group_name: str, 
                location: str, 
                topic_type_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_subscription(
                self, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_subscription_for_topic_type(
                self, 
                location: str, 
                topic_type_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.ExtensionTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ExtensionTopic: ...


    class azure.mgmt.eventgrid.aio.operations.NamespaceTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: Subscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Subscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: Subscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Subscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Subscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: SubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Subscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: SubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Subscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Subscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> Subscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> SubscriptionFullUrl: ...

        @distributed_trace
        def list_by_namespace_topic(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Subscription]: ...


    class azure.mgmt.eventgrid.aio.operations.NamespaceTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_info: NamespaceTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceTopic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_info: NamespaceTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceTopic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceTopic]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSharedAccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSharedAccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSharedAccessKeys]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_update_parameters: NamespaceTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceTopic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_update_parameters: NamespaceTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceTopic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceTopic]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> NamespaceTopic: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NamespaceTopic]: ...

        @distributed_trace_async
        async def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicSharedAccessKeys: ...


    class azure.mgmt.eventgrid.aio.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_info: Namespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_info: Namespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                regenerate_key_request: NamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceSharedAccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                regenerate_key_request: NamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceSharedAccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceSharedAccessKeys]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_update_parameters: NamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_update_parameters: NamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @distributed_trace_async
        async def begin_validate_custom_domain_ownership(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomainOwnershipValidationResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Namespace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Namespace]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Namespace]: ...

        @distributed_trace_async
        async def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NamespaceSharedAccessKeys: ...


    class azure.mgmt.eventgrid.aio.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_reconcile(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                perimeter_guid: str, 
                association_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityPerimeterConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                perimeter_guid: str, 
                association_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.eventgrid.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def authorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        async def authorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        async def authorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_configuration_info: PartnerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_configuration_info: PartnerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_configuration_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerConfiguration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_configuration_update_parameters: PartnerConfigurationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_configuration_update_parameters: PartnerConfigurationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_configuration_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerConfiguration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerConfiguration]: ...

        @overload
        async def unauthorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        async def unauthorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        async def unauthorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerDestinationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def activate(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> PartnerDestination: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination: PartnerDestination, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerDestination]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination: PartnerDestination, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerDestination]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerDestination]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination_update_parameters: PartnerDestinationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerDestination]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination_update_parameters: PartnerDestinationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerDestination]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerDestination]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> PartnerDestination: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerDestination]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerDestination]: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_info: PartnerNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_info: PartnerNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerNamespace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_update_parameters: PartnerNamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerNamespace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_update_parameters: PartnerNamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerNamespace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerNamespace]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> PartnerNamespace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerNamespace]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerNamespace]: ...

        @distributed_trace_async
        async def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                regenerate_key_request: PartnerNamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                regenerate_key_request: PartnerNamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_info: PartnerRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerRegistration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_info: PartnerRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerRegistration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerRegistration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_update_parameters: PartnerRegistrationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerRegistration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_update_parameters: PartnerRegistrationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerRegistration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PartnerRegistration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                **kwargs: Any
            ) -> PartnerRegistration: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerRegistration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerRegistration]: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_partner_topic(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.PartnerTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def activate(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_info: PartnerTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_info: PartnerTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace_async
        async def deactivate(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerTopic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PartnerTopic]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_update_parameters: PartnerTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[PartnerTopic]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_update_parameters: PartnerTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[PartnerTopic]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[PartnerTopic]: ...


    class azure.mgmt.eventgrid.aio.operations.PermissionBindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                permission_binding_info: PermissionBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PermissionBinding]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                permission_binding_info: PermissionBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PermissionBinding]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                permission_binding_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PermissionBinding]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                **kwargs: Any
            ) -> PermissionBinding: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PermissionBinding]: ...


    class azure.mgmt.eventgrid.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
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
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
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
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
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
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.eventgrid.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                parent_type: str, 
                parent_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                parent_type: str, 
                parent_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.eventgrid.aio.operations.SystemTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_system_topic(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.SystemTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_info: SystemTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SystemTopic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_info: SystemTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SystemTopic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SystemTopic]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_update_parameters: SystemTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SystemTopic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_update_parameters: SystemTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SystemTopic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SystemTopic]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                **kwargs: Any
            ) -> SystemTopic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SystemTopic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SystemTopic]: ...


    class azure.mgmt.eventgrid.aio.operations.TopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EventSubscription]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace_async
        async def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace_async
        async def get_full_url(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.aio.operations.TopicSpacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                topic_space_info: TopicSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSpace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                topic_space_info: TopicSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSpace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                topic_space_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSpace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                **kwargs: Any
            ) -> TopicSpace: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TopicSpace]: ...


    class azure.mgmt.eventgrid.aio.operations.TopicTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                topic_type_name: str, 
                **kwargs: Any
            ) -> TopicTypeInfo: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[TopicTypeInfo]: ...

        @distributed_trace
        def list_event_types(
                self, 
                topic_type_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventType]: ...


    class azure.mgmt.eventgrid.aio.operations.TopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_info: Topic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Topic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_info: Topic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Topic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Topic]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSharedAccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSharedAccessKeys]: ...

        @overload
        async def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TopicSharedAccessKeys]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_update_parameters: TopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Topic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_update_parameters: TopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Topic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Topic]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> Topic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Topic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Topic]: ...

        @distributed_trace
        def list_event_types(
                self, 
                resource_group_name: str, 
                provider_namespace: str, 
                resource_type_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventType]: ...

        @distributed_trace_async
        async def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicSharedAccessKeys: ...


    class azure.mgmt.eventgrid.aio.operations.VerifiedPartnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                verified_partner_name: str, 
                **kwargs: Any
            ) -> VerifiedPartner: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VerifiedPartner]: ...


namespace azure.mgmt.eventgrid.models

    class azure.mgmt.eventgrid.models.AdvancedFilter(_Model):
        key: Optional[str]
        operator_type: str

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                operator_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.AdvancedFilterOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL_EQUALS = "BoolEquals"
        IS_NOT_NULL = "IsNotNull"
        IS_NULL_OR_UNDEFINED = "IsNullOrUndefined"
        NUMBER_GREATER_THAN = "NumberGreaterThan"
        NUMBER_GREATER_THAN_OR_EQUALS = "NumberGreaterThanOrEquals"
        NUMBER_IN = "NumberIn"
        NUMBER_IN_RANGE = "NumberInRange"
        NUMBER_LESS_THAN = "NumberLessThan"
        NUMBER_LESS_THAN_OR_EQUALS = "NumberLessThanOrEquals"
        NUMBER_NOT_IN = "NumberNotIn"
        NUMBER_NOT_IN_RANGE = "NumberNotInRange"
        STRING_BEGINS_WITH = "StringBeginsWith"
        STRING_CONTAINS = "StringContains"
        STRING_ENDS_WITH = "StringEndsWith"
        STRING_IN = "StringIn"
        STRING_NOT_BEGINS_WITH = "StringNotBeginsWith"
        STRING_NOT_CONTAINS = "StringNotContains"
        STRING_NOT_ENDS_WITH = "StringNotEndsWith"
        STRING_NOT_IN = "StringNotIn"


    class azure.mgmt.eventgrid.models.AlternativeAuthenticationNameSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_CERTIFICATE_DNS = "ClientCertificateDns"
        CLIENT_CERTIFICATE_EMAIL = "ClientCertificateEmail"
        CLIENT_CERTIFICATE_IP = "ClientCertificateIp"
        CLIENT_CERTIFICATE_SUBJECT = "ClientCertificateSubject"
        CLIENT_CERTIFICATE_URI = "ClientCertificateUri"


    class azure.mgmt.eventgrid.models.AutoScaleConfiguration(_Model):
        enable_auto_scale: Optional[bool]
        maximum_throughput_units: Optional[int]
        minimum_throughput_units: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enable_auto_scale: Optional[bool] = ..., 
                maximum_throughput_units: Optional[int] = ..., 
                minimum_throughput_units: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.AzureADPartnerClientAuthentication(PartnerClientAuthentication, discriminator='AzureAD'):
        client_authentication_type: Literal[PartnerClientAuthenticationType.AZURE_AD]
        properties: Optional[AzureADPartnerClientAuthenticationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureADPartnerClientAuthenticationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.AzureADPartnerClientAuthenticationProperties(_Model):
        azure_active_directory_application_id_or_uri: Optional[str]
        azure_active_directory_tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_active_directory_application_id_or_uri: Optional[str] = ..., 
                azure_active_directory_tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.AzureFunctionEventSubscriptionDestination(EventSubscriptionDestination, discriminator='AzureFunction'):
        endpoint_type: Literal[EndpointType.AZURE_FUNCTION]
        properties: Optional[AzureFunctionEventSubscriptionDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureFunctionEventSubscriptionDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.AzureFunctionEventSubscriptionDestinationProperties(_Model):
        delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]]
        max_events_per_batch: Optional[int]
        preferred_batch_size_in_kilobytes: Optional[int]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]] = ..., 
                max_events_per_batch: Optional[int] = ..., 
                preferred_batch_size_in_kilobytes: Optional[int] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.BoolEqualsAdvancedFilter(AdvancedFilter, discriminator='BoolEquals'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.BOOL_EQUALS]
        value: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.BoolEqualsFilter(Filter, discriminator='BoolEquals'):
        key: str
        operator_type: Literal[FilterOperatorType.BOOL_EQUALS]
        value: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.CaCertificate(ProxyResource):
        id: str
        name: str
        properties: Optional[CaCertificateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CaCertificateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.CaCertificateProperties(_Model):
        description: Optional[str]
        encoded_certificate: Optional[str]
        expiry_time_in_utc: Optional[datetime]
        issue_time_in_utc: Optional[datetime]
        provisioning_state: Optional[Union[str, CaCertificateProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                encoded_certificate: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.CaCertificateProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.Channel(ProxyResource):
        id: str
        name: str
        properties: Optional[ChannelProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChannelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.ChannelProperties(_Model):
        channel_type: Optional[Union[str, ChannelType]]
        expiration_time_if_not_activated_utc: Optional[datetime]
        message_for_activation: Optional[str]
        partner_destination_info: Optional[PartnerDestinationInfo]
        partner_topic_info: Optional[PartnerTopicInfo]
        provisioning_state: Optional[Union[str, ChannelProvisioningState]]
        readiness_state: Optional[Union[str, ReadinessState]]

        @overload
        def __init__(
                self, 
                *, 
                channel_type: Optional[Union[str, ChannelType]] = ..., 
                expiration_time_if_not_activated_utc: Optional[datetime] = ..., 
                message_for_activation: Optional[str] = ..., 
                partner_destination_info: Optional[PartnerDestinationInfo] = ..., 
                partner_topic_info: Optional[PartnerTopicInfo] = ..., 
                provisioning_state: Optional[Union[str, ChannelProvisioningState]] = ..., 
                readiness_state: Optional[Union[str, ReadinessState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ChannelProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        IDLE_DUE_TO_MIRRORED_PARTNER_DESTINATION_DELETION = "IdleDueToMirroredPartnerDestinationDeletion"
        IDLE_DUE_TO_MIRRORED_PARTNER_TOPIC_DELETION = "IdleDueToMirroredPartnerTopicDeletion"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.ChannelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PARTNER_DESTINATION = "PartnerDestination"
        PARTNER_TOPIC = "PartnerTopic"


    class azure.mgmt.eventgrid.models.ChannelUpdateParameters(_Model):
        properties: Optional[ChannelUpdateParametersProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChannelUpdateParametersProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.ChannelUpdateParametersProperties(_Model):
        expiration_time_if_not_activated_utc: Optional[datetime]
        partner_destination_info: Optional[PartnerUpdateDestinationInfo]
        partner_topic_info: Optional[PartnerUpdateTopicInfo]

        @overload
        def __init__(
                self, 
                *, 
                expiration_time_if_not_activated_utc: Optional[datetime] = ..., 
                partner_destination_info: Optional[PartnerUpdateDestinationInfo] = ..., 
                partner_topic_info: Optional[PartnerUpdateTopicInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.Client(ProxyResource):
        id: str
        name: str
        properties: Optional[ClientProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClientProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.ClientAuthenticationSettings(_Model):
        alternative_authentication_name_sources: Optional[list[Union[str, AlternativeAuthenticationNameSource]]]
        custom_jwt_authentication: Optional[CustomJwtAuthenticationSettings]
        webhook_authentication: Optional[WebhookAuthenticationSettings]

        @overload
        def __init__(
                self, 
                *, 
                alternative_authentication_name_sources: Optional[list[Union[str, AlternativeAuthenticationNameSource]]] = ..., 
                custom_jwt_authentication: Optional[CustomJwtAuthenticationSettings] = ..., 
                webhook_authentication: Optional[WebhookAuthenticationSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ClientCertificateAuthentication(_Model):
        allowed_thumbprints: Optional[list[str]]
        validation_scheme: Optional[Union[str, ClientCertificateValidationScheme]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_thumbprints: Optional[list[str]] = ..., 
                validation_scheme: Optional[Union[str, ClientCertificateValidationScheme]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ClientCertificateValidationScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DNS_MATCHES_AUTHENTICATION_NAME = "DnsMatchesAuthenticationName"
        EMAIL_MATCHES_AUTHENTICATION_NAME = "EmailMatchesAuthenticationName"
        IP_MATCHES_AUTHENTICATION_NAME = "IpMatchesAuthenticationName"
        SUBJECT_MATCHES_AUTHENTICATION_NAME = "SubjectMatchesAuthenticationName"
        THUMBPRINT_MATCH = "ThumbprintMatch"
        URI_MATCHES_AUTHENTICATION_NAME = "UriMatchesAuthenticationName"


    class azure.mgmt.eventgrid.models.ClientGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[ClientGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClientGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.ClientGroupProperties(_Model):
        description: Optional[str]
        provisioning_state: Optional[Union[str, ClientGroupProvisioningState]]
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ClientGroupProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.ClientProperties(_Model):
        attributes: Optional[dict[str, Any]]
        authentication_name: Optional[str]
        client_certificate_authentication: Optional[ClientCertificateAuthentication]
        description: Optional[str]
        provisioning_state: Optional[Union[str, ClientProvisioningState]]
        state: Optional[Union[str, ClientState]]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[dict[str, Any]] = ..., 
                authentication_name: Optional[str] = ..., 
                client_certificate_authentication: Optional[ClientCertificateAuthentication] = ..., 
                description: Optional[str] = ..., 
                state: Optional[Union[str, ClientState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ClientProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.ClientState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.eventgrid.models.ConfidentialCompute(_Model):
        mode: Union[str, ConfidentialComputeMode]

        @overload
        def __init__(
                self, 
                *, 
                mode: Union[str, ConfidentialComputeMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ConfidentialComputeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.eventgrid.models.ConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PersistedConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PersistedConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.eventgrid.models.CustomDomainConfiguration(_Model):
        certificate_url: Optional[str]
        expected_txt_record_name: Optional[str]
        expected_txt_record_value: Optional[str]
        fully_qualified_domain_name: str
        identity: Optional[CustomDomainIdentity]
        validation_state: Optional[Union[str, CustomDomainValidationState]]

        @overload
        def __init__(
                self, 
                *, 
                certificate_url: Optional[str] = ..., 
                expected_txt_record_name: Optional[str] = ..., 
                expected_txt_record_value: Optional[str] = ..., 
                fully_qualified_domain_name: str, 
                identity: Optional[CustomDomainIdentity] = ..., 
                validation_state: Optional[Union[str, CustomDomainValidationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.CustomDomainIdentity(_Model):
        type: Optional[Union[str, CustomDomainIdentityType]]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, CustomDomainIdentityType]] = ..., 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.CustomDomainIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.CustomDomainOwnershipValidationResult(_Model):
        custom_domains_for_topic_spaces_configuration: Optional[list[CustomDomainConfiguration]]
        custom_domains_for_topics_configuration: Optional[list[CustomDomainConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                custom_domains_for_topic_spaces_configuration: Optional[list[CustomDomainConfiguration]] = ..., 
                custom_domains_for_topics_configuration: Optional[list[CustomDomainConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.CustomDomainValidationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        ERROR_RETRIEVING_DNS_RECORD = "ErrorRetrievingDnsRecord"
        PENDING = "Pending"


    class azure.mgmt.eventgrid.models.CustomJwtAuthenticationManagedIdentity(_Model):
        type: Union[str, CustomJwtAuthenticationManagedIdentityType]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, CustomJwtAuthenticationManagedIdentityType], 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.CustomJwtAuthenticationManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.CustomJwtAuthenticationSettings(_Model):
        encoded_issuer_certificates: Optional[list[EncodedIssuerCertificateInfo]]
        issuer_certificates: Optional[list[IssuerCertificateInfo]]
        token_issuer: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encoded_issuer_certificates: Optional[list[EncodedIssuerCertificateInfo]] = ..., 
                issuer_certificates: Optional[list[IssuerCertificateInfo]] = ..., 
                token_issuer: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.CustomWebhookAuthenticationManagedIdentity(_Model):
        type: Union[str, CustomWebhookAuthenticationManagedIdentityType]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, CustomWebhookAuthenticationManagedIdentityType], 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.CustomWebhookAuthenticationManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.CustomerManagedKeyEncryption(_Model):
        key_encryption_key_identity: Optional[KeyEncryptionKeyIdentity]
        key_encryption_key_status: Optional[Union[str, KeyEncryptionKeyStatus]]
        key_encryption_key_status_friendly_description: Optional[str]
        key_encryption_key_url: str

        @overload
        def __init__(
                self, 
                *, 
                key_encryption_key_identity: Optional[KeyEncryptionKeyIdentity] = ..., 
                key_encryption_key_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DataResidencyBoundary(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WITHIN_GEOPAIR = "WithinGeopair"
        WITHIN_REGION = "WithinRegion"


    class azure.mgmt.eventgrid.models.DeadLetterDestination(_Model):
        endpoint_type: str

        @overload
        def __init__(
                self, 
                *, 
                endpoint_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DeadLetterEndPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STORAGE_BLOB = "StorageBlob"


    class azure.mgmt.eventgrid.models.DeadLetterWithResourceIdentity(_Model):
        dead_letter_destination: Optional[DeadLetterDestination]
        identity: Optional[EventSubscriptionIdentity]

        @overload
        def __init__(
                self, 
                *, 
                dead_letter_destination: Optional[DeadLetterDestination] = ..., 
                identity: Optional[EventSubscriptionIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DeliveryAttributeListResult(_Model):
        value: Optional[list[DeliveryAttributeMapping]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[DeliveryAttributeMapping]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DeliveryAttributeMapping(_Model):
        name: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DeliveryAttributeMappingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.eventgrid.models.DeliveryConfiguration(_Model):
        delivery_mode: Optional[Union[str, DeliveryMode]]
        push: Optional[PushInfo]
        queue: Optional[QueueInfo]

        @overload
        def __init__(
                self, 
                *, 
                delivery_mode: Optional[Union[str, DeliveryMode]] = ..., 
                push: Optional[PushInfo] = ..., 
                queue: Optional[QueueInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DeliveryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PUSH = "Push"
        QUEUE = "Queue"


    class azure.mgmt.eventgrid.models.DeliverySchema(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_EVENT_SCHEMA_V1_0 = "CloudEventSchemaV1_0"


    class azure.mgmt.eventgrid.models.DeliveryWithResourceIdentity(_Model):
        destination: Optional[EventSubscriptionDestination]
        identity: Optional[EventSubscriptionIdentity]

        @overload
        def __init__(
                self, 
                *, 
                destination: Optional[EventSubscriptionDestination] = ..., 
                identity: Optional[EventSubscriptionIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.Domain(TrackedResource):
        id: str
        identity: Optional[IdentityInfo]
        location: str
        name: str
        properties: Optional[DomainProperties]
        sku: Optional[ResourceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                location: str, 
                properties: Optional[DomainProperties] = ..., 
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


    class azure.mgmt.eventgrid.models.DomainProperties(_Model):
        auto_create_topic_with_first_subscription: Optional[bool]
        auto_delete_topic_with_last_subscription: Optional[bool]
        data_residency_boundary: Optional[Union[str, DataResidencyBoundary]]
        disable_local_auth: Optional[bool]
        endpoint: Optional[str]
        event_type_info: Optional[EventTypeInfo]
        inbound_ip_rules: Optional[list[InboundIpRule]]
        input_schema: Optional[Union[str, InputSchema]]
        input_schema_mapping: Optional[InputSchemaMapping]
        metric_resource_id: Optional[str]
        minimum_tls_version_allowed: Optional[Union[str, TlsVersion]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, DomainProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                auto_create_topic_with_first_subscription: Optional[bool] = ..., 
                auto_delete_topic_with_last_subscription: Optional[bool] = ..., 
                data_residency_boundary: Optional[Union[str, DataResidencyBoundary]] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                event_type_info: Optional[EventTypeInfo] = ..., 
                inbound_ip_rules: Optional[list[InboundIpRule]] = ..., 
                input_schema: Optional[Union[str, InputSchema]] = ..., 
                input_schema_mapping: Optional[InputSchemaMapping] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DomainProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.DomainRegenerateKeyRequest(_Model):
        key_name: str

        @overload
        def __init__(
                self, 
                *, 
                key_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DomainSharedAccessKeys(_Model):
        key1: Optional[str]
        key2: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key1: Optional[str] = ..., 
                key2: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DomainTopic(ProxyResource):
        id: str
        name: str
        properties: Optional[DomainTopicProperties]
        system_data: SystemData
        type: str


    class azure.mgmt.eventgrid.models.DomainTopicProperties(_Model):
        provisioning_state: Optional[Union[str, DomainTopicProvisioningState]]


    class azure.mgmt.eventgrid.models.DomainTopicProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.DomainUpdateParameterProperties(_Model):
        auto_create_topic_with_first_subscription: Optional[bool]
        auto_delete_topic_with_last_subscription: Optional[bool]
        data_residency_boundary: Optional[Union[str, DataResidencyBoundary]]
        disable_local_auth: Optional[bool]
        event_type_info: Optional[EventTypeInfo]
        inbound_ip_rules: Optional[list[InboundIpRule]]
        minimum_tls_version_allowed: Optional[Union[str, TlsVersion]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                auto_create_topic_with_first_subscription: Optional[bool] = ..., 
                auto_delete_topic_with_last_subscription: Optional[bool] = ..., 
                data_residency_boundary: Optional[Union[str, DataResidencyBoundary]] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                event_type_info: Optional[EventTypeInfo] = ..., 
                inbound_ip_rules: Optional[list[InboundIpRule]] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DomainUpdateParameters(_Model):
        identity: Optional[IdentityInfo]
        properties: Optional[DomainUpdateParameterProperties]
        sku: Optional[ResourceSku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                properties: Optional[DomainUpdateParameterProperties] = ..., 
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


    class azure.mgmt.eventgrid.models.DynamicDeliveryAttributeMapping(DeliveryAttributeMapping, discriminator='Dynamic'):
        name: str
        properties: Optional[DynamicDeliveryAttributeMappingProperties]
        type: Literal[DeliveryAttributeMappingType.DYNAMIC]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[DynamicDeliveryAttributeMappingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.DynamicDeliveryAttributeMappingProperties(_Model):
        source_field: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_field: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.DynamicRoutingEnrichment(_Model):
        key: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EncodedIssuerCertificateInfo(_Model):
        encoded_certificate: str
        kid: str

        @overload
        def __init__(
                self, 
                *, 
                encoded_certificate: str, 
                kid: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FUNCTION = "AzureFunction"
        EVENT_HUB = "EventHub"
        HYBRID_CONNECTION = "HybridConnection"
        MONITOR_ALERT = "MonitorAlert"
        NAMESPACE_TOPIC = "NamespaceTopic"
        PARTNER_DESTINATION = "PartnerDestination"
        SERVICE_BUS_QUEUE = "ServiceBusQueue"
        SERVICE_BUS_TOPIC = "ServiceBusTopic"
        STORAGE_QUEUE = "StorageQueue"
        WEB_HOOK = "WebHook"


    class azure.mgmt.eventgrid.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.eventgrid.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.eventgrid.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EventDefinitionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "Inline"


    class azure.mgmt.eventgrid.models.EventDeliverySchema(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_EVENT_SCHEMA_V1_0 = "CloudEventSchemaV1_0"
        CUSTOM_INPUT_SCHEMA = "CustomInputSchema"
        EVENT_GRID_SCHEMA = "EventGridSchema"


    class azure.mgmt.eventgrid.models.EventHubEventSubscriptionDestination(EventSubscriptionDestination, discriminator='EventHub'):
        endpoint_type: Literal[EndpointType.EVENT_HUB]
        properties: Optional[EventHubEventSubscriptionDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EventHubEventSubscriptionDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.EventHubEventSubscriptionDestinationProperties(_Model):
        delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EventInputSchema(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_EVENT_SCHEMA_V1_0 = "CloudEventSchemaV1_0"


    class azure.mgmt.eventgrid.models.EventSubscription(ProxyResource):
        id: str
        name: str
        properties: Optional[EventSubscriptionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EventSubscriptionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.EventSubscriptionDestination(_Model):
        endpoint_type: str

        @overload
        def __init__(
                self, 
                *, 
                endpoint_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EventSubscriptionFilter(_Model):
        advanced_filters: Optional[list[AdvancedFilter]]
        enable_advanced_filtering_on_arrays: Optional[bool]
        included_event_types: Optional[list[str]]
        is_subject_case_sensitive: Optional[bool]
        subject_begins_with: Optional[str]
        subject_ends_with: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                advanced_filters: Optional[list[AdvancedFilter]] = ..., 
                enable_advanced_filtering_on_arrays: Optional[bool] = ..., 
                included_event_types: Optional[list[str]] = ..., 
                is_subject_case_sensitive: Optional[bool] = ..., 
                subject_begins_with: Optional[str] = ..., 
                subject_ends_with: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EventSubscriptionFullUrl(_Model):
        endpoint_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EventSubscriptionIdentity(_Model):
        federated_identity_credential_info: Optional[FederatedIdentityCredentialInfo]
        type: Optional[Union[str, EventSubscriptionIdentityType]]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                federated_identity_credential_info: Optional[FederatedIdentityCredentialInfo] = ..., 
                type: Optional[Union[str, EventSubscriptionIdentityType]] = ..., 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EventSubscriptionIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.EventSubscriptionProperties(_Model):
        dead_letter_destination: Optional[DeadLetterDestination]
        dead_letter_with_resource_identity: Optional[DeadLetterWithResourceIdentity]
        delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity]
        destination: Optional[EventSubscriptionDestination]
        event_delivery_schema: Optional[Union[str, EventDeliverySchema]]
        expiration_time_utc: Optional[datetime]
        filter: Optional[EventSubscriptionFilter]
        labels: Optional[list[str]]
        provisioning_state: Optional[Union[str, EventSubscriptionProvisioningState]]
        retry_policy: Optional[RetryPolicy]
        topic: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dead_letter_destination: Optional[DeadLetterDestination] = ..., 
                dead_letter_with_resource_identity: Optional[DeadLetterWithResourceIdentity] = ..., 
                delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity] = ..., 
                destination: Optional[EventSubscriptionDestination] = ..., 
                event_delivery_schema: Optional[Union[str, EventDeliverySchema]] = ..., 
                expiration_time_utc: Optional[datetime] = ..., 
                filter: Optional[EventSubscriptionFilter] = ..., 
                labels: Optional[list[str]] = ..., 
                retry_policy: Optional[RetryPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EventSubscriptionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWAITING_MANUAL_ACTION = "AwaitingManualAction"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.EventSubscriptionUpdateParameters(_Model):
        dead_letter_destination: Optional[DeadLetterDestination]
        dead_letter_with_resource_identity: Optional[DeadLetterWithResourceIdentity]
        delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity]
        destination: Optional[EventSubscriptionDestination]
        event_delivery_schema: Optional[Union[str, EventDeliverySchema]]
        expiration_time_utc: Optional[datetime]
        filter: Optional[EventSubscriptionFilter]
        labels: Optional[list[str]]
        retry_policy: Optional[RetryPolicy]

        @overload
        def __init__(
                self, 
                *, 
                dead_letter_destination: Optional[DeadLetterDestination] = ..., 
                dead_letter_with_resource_identity: Optional[DeadLetterWithResourceIdentity] = ..., 
                delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity] = ..., 
                destination: Optional[EventSubscriptionDestination] = ..., 
                event_delivery_schema: Optional[Union[str, EventDeliverySchema]] = ..., 
                expiration_time_utc: Optional[datetime] = ..., 
                filter: Optional[EventSubscriptionFilter] = ..., 
                labels: Optional[list[str]] = ..., 
                retry_policy: Optional[RetryPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EventType(Resource):
        id: str
        name: str
        properties: Optional[EventTypeProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EventTypeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.EventTypeInfo(_Model):
        inline_event_types: Optional[dict[str, InlineEventProperties]]
        kind: Optional[Union[str, EventDefinitionKind]]

        @overload
        def __init__(
                self, 
                *, 
                inline_event_types: Optional[dict[str, InlineEventProperties]] = ..., 
                kind: Optional[Union[str, EventDefinitionKind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.EventTypeProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        is_in_default_set: Optional[bool]
        schema_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                is_in_default_set: Optional[bool] = ..., 
                schema_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ExtendedLocation(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.eventgrid.models.ExtensionTopic(ExtensionResource):
        id: str
        name: str
        properties: Optional[ExtensionTopicProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExtensionTopicProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.ExtensionTopicProperties(_Model):
        description: Optional[str]
        system_topic: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                system_topic: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.FederatedIdentityCredentialInfo(_Model):
        federated_client_id: str

        @overload
        def __init__(
                self, 
                *, 
                federated_client_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.Filter(_Model):
        key: Optional[str]
        operator_type: str

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                operator_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.FilterOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL_EQUALS = "BoolEquals"
        IS_NOT_NULL = "IsNotNull"
        IS_NULL_OR_UNDEFINED = "IsNullOrUndefined"
        NUMBER_GREATER_THAN = "NumberGreaterThan"
        NUMBER_GREATER_THAN_OR_EQUALS = "NumberGreaterThanOrEquals"
        NUMBER_IN = "NumberIn"
        NUMBER_IN_RANGE = "NumberInRange"
        NUMBER_LESS_THAN = "NumberLessThan"
        NUMBER_LESS_THAN_OR_EQUALS = "NumberLessThanOrEquals"
        NUMBER_NOT_IN = "NumberNotIn"
        NUMBER_NOT_IN_RANGE = "NumberNotInRange"
        STRING_BEGINS_WITH = "StringBeginsWith"
        STRING_CONTAINS = "StringContains"
        STRING_ENDS_WITH = "StringEndsWith"
        STRING_IN = "StringIn"
        STRING_NOT_BEGINS_WITH = "StringNotBeginsWith"
        STRING_NOT_CONTAINS = "StringNotContains"
        STRING_NOT_ENDS_WITH = "StringNotEndsWith"
        STRING_NOT_IN = "StringNotIn"


    class azure.mgmt.eventgrid.models.FiltersConfiguration(_Model):
        filters: Optional[list[Filter]]
        included_event_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                filters: Optional[list[Filter]] = ..., 
                included_event_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.HybridConnectionEventSubscriptionDestination(EventSubscriptionDestination, discriminator='HybridConnection'):
        endpoint_type: Literal[EndpointType.HYBRID_CONNECTION]
        properties: Optional[HybridConnectionEventSubscriptionDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HybridConnectionEventSubscriptionDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.HybridConnectionEventSubscriptionDestinationProperties(_Model):
        delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.IdentityInfo(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, IdentityType]]
        user_assigned_identities: Optional[dict[str, UserIdentityProperties]]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                type: Optional[Union[str, IdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserIdentityProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.InboundIpRule(_Model):
        action: Optional[Union[str, IpActionType]]
        ip_mask: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, IpActionType]] = ..., 
                ip_mask: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.InlineEventProperties(_Model):
        data_schema_url: Optional[str]
        description: Optional[str]
        display_name: Optional[str]
        documentation_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_schema_url: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                documentation_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.InputSchema(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_EVENT_SCHEMA_V1_0 = "CloudEventSchemaV1_0"
        CUSTOM_EVENT_SCHEMA = "CustomEventSchema"
        EVENT_GRID_SCHEMA = "EventGridSchema"


    class azure.mgmt.eventgrid.models.InputSchemaMapping(_Model):
        input_schema_mapping_type: str

        @overload
        def __init__(
                self, 
                *, 
                input_schema_mapping_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.InputSchemaMappingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "Json"


    class azure.mgmt.eventgrid.models.IpActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"


    class azure.mgmt.eventgrid.models.IpAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DUAL_STACK = "DualStack"
        I_PV4 = "IPv4"


    class azure.mgmt.eventgrid.models.IsNotNullAdvancedFilter(AdvancedFilter, discriminator='IsNotNull'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.IS_NOT_NULL]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.IsNotNullFilter(Filter, discriminator='IsNotNull'):
        key: str
        operator_type: Literal[FilterOperatorType.IS_NOT_NULL]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.IsNullOrUndefinedAdvancedFilter(AdvancedFilter, discriminator='IsNullOrUndefined'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.IS_NULL_OR_UNDEFINED]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.IsNullOrUndefinedFilter(Filter, discriminator='IsNullOrUndefined'):
        key: str
        operator_type: Literal[FilterOperatorType.IS_NULL_OR_UNDEFINED]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.IssuerCertificateInfo(_Model):
        certificate_url: str
        identity: Optional[CustomJwtAuthenticationManagedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                certificate_url: str, 
                identity: Optional[CustomJwtAuthenticationManagedIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.JsonField(_Model):
        source_field: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_field: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.JsonFieldWithDefault(_Model):
        default_value: Optional[str]
        source_field: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default_value: Optional[str] = ..., 
                source_field: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.JsonInputSchemaMapping(InputSchemaMapping, discriminator='Json'):
        input_schema_mapping_type: Literal[InputSchemaMappingType.JSON]
        properties: Optional[JsonInputSchemaMappingProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JsonInputSchemaMappingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.JsonInputSchemaMappingProperties(_Model):
        data_version: Optional[JsonFieldWithDefault]
        event_time: Optional[JsonField]
        event_type: Optional[JsonFieldWithDefault]
        id: Optional[JsonField]
        subject: Optional[JsonFieldWithDefault]
        topic: Optional[JsonField]

        @overload
        def __init__(
                self, 
                *, 
                data_version: Optional[JsonFieldWithDefault] = ..., 
                event_time: Optional[JsonField] = ..., 
                event_type: Optional[JsonFieldWithDefault] = ..., 
                id: Optional[JsonField] = ..., 
                subject: Optional[JsonFieldWithDefault] = ..., 
                topic: Optional[JsonField] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.KeyEncryption(_Model):
        customer_managed_key_encryption: list[CustomerManagedKeyEncryption]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_key_encryption: list[CustomerManagedKeyEncryption]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.KeyEncryptionIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.KeyEncryptionKeyIdentity(_Model):
        type: Union[str, KeyEncryptionIdentityType]
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, KeyEncryptionIdentityType], 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.KeyEncryptionKeyStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        REVOKED = "Revoked"


    class azure.mgmt.eventgrid.models.MonitorAlertEventSubscriptionDestination(EventSubscriptionDestination, discriminator='MonitorAlert'):
        endpoint_type: Literal[EndpointType.MONITOR_ALERT]
        properties: Optional[MonitorAlertEventSubscriptionDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MonitorAlertEventSubscriptionDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.MonitorAlertEventSubscriptionDestinationProperties(_Model):
        action_groups: Optional[list[str]]
        description: Optional[str]
        severity: Optional[Union[str, MonitorAlertSeverity]]

        @overload
        def __init__(
                self, 
                *, 
                action_groups: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                severity: Optional[Union[str, MonitorAlertSeverity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.MonitorAlertSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEV0 = "Sev0"
        SEV1 = "Sev1"
        SEV2 = "Sev2"
        SEV3 = "Sev3"
        SEV4 = "Sev4"


    class azure.mgmt.eventgrid.models.Namespace(TrackedResource):
        id: str
        identity: Optional[IdentityInfo]
        location: str
        name: str
        properties: Optional[NamespaceProperties]
        sku: Optional[NamespaceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                location: str, 
                properties: Optional[NamespaceProperties] = ..., 
                sku: Optional[NamespaceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceProperties(_Model):
        auto_scale_configuration: Optional[AutoScaleConfiguration]
        inbound_ip_rules: Optional[list[InboundIpRule]]
        ip_address_type: Optional[Union[str, IpAddressType]]
        is_zone_redundant: Optional[bool]
        minimum_tls_version_allowed: Optional[Union[str, TlsVersion]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, NamespaceProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        topic_spaces_configuration: Optional[TopicSpacesConfiguration]
        topics_configuration: Optional[TopicsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                auto_scale_configuration: Optional[AutoScaleConfiguration] = ..., 
                inbound_ip_rules: Optional[list[InboundIpRule]] = ..., 
                ip_address_type: Optional[Union[str, IpAddressType]] = ..., 
                is_zone_redundant: Optional[bool] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                private_endpoint_connections: Optional[list[PrivateEndpointConnection]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                topic_spaces_configuration: Optional[TopicSpacesConfiguration] = ..., 
                topics_configuration: Optional[TopicsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATE_FAILED = "CreateFailed"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETE_FAILED = "DeleteFailed"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATED_FAILED = "UpdatedFailed"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.NamespaceRegenerateKeyRequest(_Model):
        key_name: str

        @overload
        def __init__(
                self, 
                *, 
                key_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceSharedAccessKeys(_Model):
        key1: Optional[str]
        key2: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key1: Optional[str] = ..., 
                key2: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceSku(_Model):
        capacity: Optional[int]
        name: Optional[Union[str, SkuName]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Optional[Union[str, SkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceTopic(ProxyResource):
        id: str
        name: str
        properties: Optional[NamespaceTopicProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NamespaceTopicProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceTopicEventSubscriptionDestination(EventSubscriptionDestination, discriminator='NamespaceTopic'):
        endpoint_type: Literal[EndpointType.NAMESPACE_TOPIC]
        properties: Optional[NamespaceTopicEventSubscriptionDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NamespaceTopicEventSubscriptionDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceTopicEventSubscriptionDestinationProperties(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceTopicProperties(_Model):
        event_retention_in_days: Optional[int]
        input_schema: Optional[Union[str, EventInputSchema]]
        provisioning_state: Optional[Union[str, NamespaceTopicProvisioningState]]
        publisher_type: Optional[Union[str, PublisherType]]

        @overload
        def __init__(
                self, 
                *, 
                event_retention_in_days: Optional[int] = ..., 
                input_schema: Optional[Union[str, EventInputSchema]] = ..., 
                publisher_type: Optional[Union[str, PublisherType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceTopicProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATE_FAILED = "CreateFailed"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETE_FAILED = "DeleteFailed"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATED_FAILED = "UpdatedFailed"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.NamespaceTopicUpdateParameterProperties(_Model):
        event_retention_in_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                event_retention_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceTopicUpdateParameters(_Model):
        properties: Optional[NamespaceTopicUpdateParameterProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NamespaceTopicUpdateParameterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceUpdateParameterProperties(_Model):
        auto_scale_configuration: Optional[UpdateAutoScaleConfiguration]
        inbound_ip_rules: Optional[list[InboundIpRule]]
        ip_address_type: Optional[Union[str, IpAddressType]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        topic_spaces_configuration: Optional[UpdateTopicSpacesConfigurationInfo]
        topics_configuration: Optional[UpdateTopicsConfigurationInfo]

        @overload
        def __init__(
                self, 
                *, 
                auto_scale_configuration: Optional[UpdateAutoScaleConfiguration] = ..., 
                inbound_ip_rules: Optional[list[InboundIpRule]] = ..., 
                ip_address_type: Optional[Union[str, IpAddressType]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                topic_spaces_configuration: Optional[UpdateTopicSpacesConfigurationInfo] = ..., 
                topics_configuration: Optional[UpdateTopicsConfigurationInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NamespaceUpdateParameters(_Model):
        identity: Optional[IdentityInfo]
        properties: Optional[NamespaceUpdateParameterProperties]
        sku: Optional[NamespaceSku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                properties: Optional[NamespaceUpdateParameterProperties] = ..., 
                sku: Optional[NamespaceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"
        LEARNING = "Learning"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkSecurityPerimeterConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkSecurityPerimeterConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationIssueSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationIssueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_PROPAGATION_FAILURE = "ConfigurationPropagationFailure"
        MISSING_IDENTITY_CONFIGURATION = "MissingIdentityConfiguration"
        MISSING_PERIMETER_CONFIGURATION = "MissingPerimeterConfiguration"
        OTHER = "Other"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationIssues(_Model):
        name: Optional[str]
        properties: Optional[NetworkSecurityPerimeterConfigurationIssuesProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[NetworkSecurityPerimeterConfigurationIssuesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationIssuesProperties(_Model):
        description: Optional[str]
        issue_type: Optional[Union[str, NetworkSecurityPerimeterConfigurationIssueType]]
        severity: Optional[Union[str, NetworkSecurityPerimeterConfigurationIssueSeverity]]
        suggested_access_rules: Optional[list[str]]
        suggested_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                issue_type: Optional[Union[str, NetworkSecurityPerimeterConfigurationIssueType]] = ..., 
                severity: Optional[Union[str, NetworkSecurityPerimeterConfigurationIssueSeverity]] = ..., 
                suggested_access_rules: Optional[list[str]] = ..., 
                suggested_resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationProfile(_Model):
        access_rules: Optional[list[NetworkSecurityPerimeterProfileAccessRule]]
        access_rules_version: Optional[str]
        diagnostic_settings_version: Optional[str]
        enabled_log_categories: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_rules: Optional[list[NetworkSecurityPerimeterProfileAccessRule]] = ..., 
                access_rules_version: Optional[str] = ..., 
                diagnostic_settings_version: Optional[str] = ..., 
                enabled_log_categories: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
        network_security_perimeter: Optional[NetworkSecurityPerimeterInfo]
        profile: Optional[NetworkSecurityPerimeterConfigurationProfile]
        provisioning_issues: Optional[list[NetworkSecurityPerimeterConfigurationIssues]]
        provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigProvisioningState]]
        resource_association: Optional[ResourceAssociation]

        @overload
        def __init__(
                self, 
                *, 
                network_security_perimeter: Optional[NetworkSecurityPerimeterInfo] = ..., 
                profile: Optional[NetworkSecurityPerimeterConfigurationProfile] = ..., 
                provisioning_issues: Optional[list[NetworkSecurityPerimeterConfigurationIssues]] = ..., 
                provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigProvisioningState]] = ..., 
                resource_association: Optional[ResourceAssociation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterInfo(_Model):
        id: Optional[str]
        location: Optional[str]
        perimeter_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterProfileAccessRule(_Model):
        fully_qualified_arm_id: Optional[str]
        name: Optional[str]
        properties: Optional[NetworkSecurityPerimeterProfileAccessRuleProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                fully_qualified_arm_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[NetworkSecurityPerimeterProfileAccessRuleProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterProfileAccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterProfileAccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, NetworkSecurityPerimeterProfileAccessRuleDirection]]
        email_addresses: Optional[list[str]]
        fully_qualified_domain_names: Optional[list[str]]
        network_security_perimeters: Optional[list[NetworkSecurityPerimeterInfo]]
        phone_numbers: Optional[list[str]]
        subscriptions: Optional[list[NetworkSecurityPerimeterSubscription]]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ..., 
                direction: Optional[Union[str, NetworkSecurityPerimeterProfileAccessRuleDirection]] = ..., 
                email_addresses: Optional[list[str]] = ..., 
                fully_qualified_domain_names: Optional[list[str]] = ..., 
                network_security_perimeters: Optional[list[NetworkSecurityPerimeterInfo]] = ..., 
                phone_numbers: Optional[list[str]] = ..., 
                subscriptions: Optional[list[NetworkSecurityPerimeterSubscription]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOMAINS = "domains"
        TOPICS = "topics"


    class azure.mgmt.eventgrid.models.NetworkSecurityPerimeterSubscription(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberGreaterThanAdvancedFilter(AdvancedFilter, discriminator='NumberGreaterThan'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.NUMBER_GREATER_THAN]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberGreaterThanFilter(Filter, discriminator='NumberGreaterThan'):
        key: str
        operator_type: Literal[FilterOperatorType.NUMBER_GREATER_THAN]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberGreaterThanOrEqualsAdvancedFilter(AdvancedFilter, discriminator='NumberGreaterThanOrEquals'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.NUMBER_GREATER_THAN_OR_EQUALS]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberGreaterThanOrEqualsFilter(Filter, discriminator='NumberGreaterThanOrEquals'):
        key: str
        operator_type: Literal[FilterOperatorType.NUMBER_GREATER_THAN_OR_EQUALS]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberInAdvancedFilter(AdvancedFilter, discriminator='NumberIn'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.NUMBER_IN]
        values_property: Optional[list[float]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[float]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberInFilter(Filter, discriminator='NumberIn'):
        key: str
        operator_type: Literal[FilterOperatorType.NUMBER_IN]
        values_property: Optional[list[float]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[float]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberInRangeAdvancedFilter(AdvancedFilter, discriminator='NumberInRange'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.NUMBER_IN_RANGE]
        values_property: Optional[list[list[float]]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[list[float]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberInRangeFilter(Filter, discriminator='NumberInRange'):
        key: str
        operator_type: Literal[FilterOperatorType.NUMBER_IN_RANGE]
        values_property: Optional[list[list[float]]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[list[float]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberLessThanAdvancedFilter(AdvancedFilter, discriminator='NumberLessThan'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.NUMBER_LESS_THAN]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberLessThanFilter(Filter, discriminator='NumberLessThan'):
        key: str
        operator_type: Literal[FilterOperatorType.NUMBER_LESS_THAN]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberLessThanOrEqualsAdvancedFilter(AdvancedFilter, discriminator='NumberLessThanOrEquals'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.NUMBER_LESS_THAN_OR_EQUALS]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberLessThanOrEqualsFilter(Filter, discriminator='NumberLessThanOrEquals'):
        key: str
        operator_type: Literal[FilterOperatorType.NUMBER_LESS_THAN_OR_EQUALS]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberNotInAdvancedFilter(AdvancedFilter, discriminator='NumberNotIn'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.NUMBER_NOT_IN]
        values_property: Optional[list[float]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[float]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberNotInFilter(Filter, discriminator='NumberNotIn'):
        key: str
        operator_type: Literal[FilterOperatorType.NUMBER_NOT_IN]
        values_property: Optional[list[float]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[float]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberNotInRangeAdvancedFilter(AdvancedFilter, discriminator='NumberNotInRange'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.NUMBER_NOT_IN_RANGE]
        values_property: Optional[list[list[float]]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[list[float]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.NumberNotInRangeFilter(Filter, discriminator='NumberNotInRange'):
        key: str
        operator_type: Literal[FilterOperatorType.NUMBER_NOT_IN_RANGE]
        values_property: Optional[list[list[float]]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[list[float]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.Operation(_Model):
        display: Optional[OperationInfo]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[Any]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationInfo] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.OperationInfo(_Model):
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


    class azure.mgmt.eventgrid.models.Partner(_Model):
        authorization_expiration_time_in_utc: Optional[datetime]
        partner_name: Optional[str]
        partner_registration_immutable_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authorization_expiration_time_in_utc: Optional[datetime] = ..., 
                partner_name: Optional[str] = ..., 
                partner_registration_immutable_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerAuthorization(_Model):
        authorized_partners_list: Optional[list[Partner]]
        default_maximum_expiration_time_in_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                authorized_partners_list: Optional[list[Partner]] = ..., 
                default_maximum_expiration_time_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerClientAuthentication(_Model):
        client_authentication_type: str

        @overload
        def __init__(
                self, 
                *, 
                client_authentication_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerClientAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_AD = "AzureAD"


    class azure.mgmt.eventgrid.models.PartnerConfiguration(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[PartnerConfigurationProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[PartnerConfigurationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerConfigurationProperties(_Model):
        partner_authorization: Optional[PartnerAuthorization]
        provisioning_state: Optional[Union[str, PartnerConfigurationProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                partner_authorization: Optional[PartnerAuthorization] = ..., 
                provisioning_state: Optional[Union[str, PartnerConfigurationProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PartnerConfigurationUpdateParameterProperties(_Model):
        default_maximum_expiration_time_in_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                default_maximum_expiration_time_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerConfigurationUpdateParameters(_Model):
        properties: Optional[PartnerConfigurationUpdateParameterProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PartnerConfigurationUpdateParameterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerDestination(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[PartnerDestinationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[PartnerDestinationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerDestinationActivationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        NEVER_ACTIVATED = "NeverActivated"


    class azure.mgmt.eventgrid.models.PartnerDestinationInfo(_Model):
        azure_subscription_id: Optional[str]
        endpoint_service_context: Optional[str]
        endpoint_type: str
        name: Optional[str]
        resource_group_name: Optional[str]
        resource_move_change_history: Optional[list[ResourceMoveChangeHistory]]

        @overload
        def __init__(
                self, 
                *, 
                azure_subscription_id: Optional[str] = ..., 
                endpoint_service_context: Optional[str] = ..., 
                endpoint_type: str, 
                name: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                resource_move_change_history: Optional[list[ResourceMoveChangeHistory]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerDestinationProperties(_Model):
        activation_state: Optional[Union[str, PartnerDestinationActivationState]]
        endpoint_base_url: Optional[str]
        endpoint_service_context: Optional[str]
        expiration_time_if_not_activated_utc: Optional[datetime]
        message_for_activation: Optional[str]
        partner_registration_immutable_id: Optional[str]
        provisioning_state: Optional[Union[str, PartnerDestinationProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                activation_state: Optional[Union[str, PartnerDestinationActivationState]] = ..., 
                endpoint_base_url: Optional[str] = ..., 
                endpoint_service_context: Optional[str] = ..., 
                expiration_time_if_not_activated_utc: Optional[datetime] = ..., 
                message_for_activation: Optional[str] = ..., 
                partner_registration_immutable_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerDestinationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        IDLE_DUE_TO_MIRRORED_CHANNEL_RESOURCE_DELETION = "IdleDueToMirroredChannelResourceDeletion"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PartnerDestinationUpdateParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerDetails(_Model):
        description: Optional[str]
        long_description: Optional[str]
        setup_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                long_description: Optional[str] = ..., 
                setup_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerEndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEB_HOOK = "WebHook"


    class azure.mgmt.eventgrid.models.PartnerEventSubscriptionDestination(EventSubscriptionDestination, discriminator='PartnerDestination'):
        endpoint_type: Literal[EndpointType.PARTNER_DESTINATION]
        properties: Optional[PartnerEventSubscriptionDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PartnerEventSubscriptionDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerEventSubscriptionDestinationProperties(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerNamespace(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[PartnerNamespaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[PartnerNamespaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerNamespaceProperties(_Model):
        disable_local_auth: Optional[bool]
        endpoint: Optional[str]
        inbound_ip_rules: Optional[list[InboundIpRule]]
        minimum_tls_version_allowed: Optional[Union[str, TlsVersion]]
        partner_registration_fully_qualified_id: Optional[str]
        partner_topic_routing_mode: Optional[Union[str, PartnerTopicRoutingMode]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, PartnerNamespaceProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                disable_local_auth: Optional[bool] = ..., 
                inbound_ip_rules: Optional[list[InboundIpRule]] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                partner_registration_fully_qualified_id: Optional[str] = ..., 
                partner_topic_routing_mode: Optional[Union[str, PartnerTopicRoutingMode]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerNamespaceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PartnerNamespaceRegenerateKeyRequest(_Model):
        key_name: str

        @overload
        def __init__(
                self, 
                *, 
                key_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerNamespaceSharedAccessKeys(_Model):
        key1: Optional[str]
        key2: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key1: Optional[str] = ..., 
                key2: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerNamespaceUpdateParameterProperties(_Model):
        disable_local_auth: Optional[bool]
        inbound_ip_rules: Optional[list[InboundIpRule]]
        minimum_tls_version_allowed: Optional[Union[str, TlsVersion]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                disable_local_auth: Optional[bool] = ..., 
                inbound_ip_rules: Optional[list[InboundIpRule]] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerNamespaceUpdateParameters(_Model):
        properties: Optional[PartnerNamespaceUpdateParameterProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PartnerNamespaceUpdateParameterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerRegistration(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[PartnerRegistrationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[PartnerRegistrationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerRegistrationProperties(_Model):
        partner_registration_immutable_id: Optional[str]
        provisioning_state: Optional[Union[str, PartnerRegistrationProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                partner_registration_immutable_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerRegistrationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PartnerRegistrationUpdateParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerTopic(TrackedResource):
        id: str
        identity: Optional[IdentityInfo]
        location: str
        name: str
        properties: Optional[PartnerTopicProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                location: str, 
                properties: Optional[PartnerTopicProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerTopicActivationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        DEACTIVATED = "Deactivated"
        NEVER_ACTIVATED = "NeverActivated"


    class azure.mgmt.eventgrid.models.PartnerTopicInfo(_Model):
        azure_subscription_id: Optional[str]
        event_type_info: Optional[EventTypeInfo]
        name: Optional[str]
        resource_group_name: Optional[str]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_subscription_id: Optional[str] = ..., 
                event_type_info: Optional[EventTypeInfo] = ..., 
                name: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerTopicProperties(_Model):
        activation_state: Optional[Union[str, PartnerTopicActivationState]]
        event_type_info: Optional[EventTypeInfo]
        expiration_time_if_not_activated_utc: Optional[datetime]
        message_for_activation: Optional[str]
        partner_registration_immutable_id: Optional[str]
        partner_topic_friendly_description: Optional[str]
        provisioning_state: Optional[Union[str, PartnerTopicProvisioningState]]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activation_state: Optional[Union[str, PartnerTopicActivationState]] = ..., 
                event_type_info: Optional[EventTypeInfo] = ..., 
                expiration_time_if_not_activated_utc: Optional[datetime] = ..., 
                message_for_activation: Optional[str] = ..., 
                partner_registration_immutable_id: Optional[str] = ..., 
                partner_topic_friendly_description: Optional[str] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerTopicProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        IDLE_DUE_TO_MIRRORED_CHANNEL_RESOURCE_DELETION = "IdleDueToMirroredChannelResourceDeletion"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PartnerTopicRoutingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANNEL_NAME_HEADER = "ChannelNameHeader"
        SOURCE_EVENT_ATTRIBUTE = "SourceEventAttribute"


    class azure.mgmt.eventgrid.models.PartnerTopicUpdateParameters(_Model):
        identity: Optional[IdentityInfo]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerUpdateDestinationInfo(_Model):
        endpoint_type: str

        @overload
        def __init__(
                self, 
                *, 
                endpoint_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PartnerUpdateTopicInfo(_Model):
        event_type_info: Optional[EventTypeInfo]

        @overload
        def __init__(
                self, 
                *, 
                event_type_info: Optional[EventTypeInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PermissionBinding(ProxyResource):
        id: str
        name: str
        properties: Optional[PermissionBindingProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PermissionBindingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.PermissionBindingProperties(_Model):
        client_group_name: Optional[str]
        description: Optional[str]
        permission: Optional[Union[str, PermissionType]]
        provisioning_state: Optional[Union[str, PermissionBindingProvisioningState]]
        topic_space_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_group_name: Optional[str] = ..., 
                description: Optional[str] = ..., 
                permission: Optional[Union[str, PermissionType]] = ..., 
                topic_space_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PermissionBindingProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.PermissionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PUBLISHER = "Publisher"
        SUBSCRIBER = "Subscriber"


    class azure.mgmt.eventgrid.models.PersistedConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.eventgrid.models.PlatformCapabilities(_Model):
        confidential_compute: Optional[ConfidentialCompute]

        @overload
        def __init__(
                self, 
                *, 
                confidential_compute: Optional[ConfidentialCompute] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.eventgrid.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[ConnectionState]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[str]] = ..., 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[ConnectionState] = ..., 
                provisioning_state: Optional[Union[str, ResourceProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.PrivateEndpointConnectionsParentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOMAINS = "domains"
        NAMESPACES = "namespaces"
        PARTNER_NAMESPACES = "partnerNamespaces"
        TOPICS = "topics"


    class azure.mgmt.eventgrid.models.PrivateLinkResource(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[PrivateLinkResourceProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[PrivateLinkResourceProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.PrivateLinkResourceProperties(_Model):
        display_name: Optional[str]
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                group_id: Optional[str] = ..., 
                required_members: Optional[list[str]] = ..., 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.eventgrid.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.eventgrid.models.PublisherType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"


    class azure.mgmt.eventgrid.models.PushInfo(_Model):
        dead_letter_destination_with_resource_identity: Optional[DeadLetterWithResourceIdentity]
        delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity]
        destination: Optional[EventSubscriptionDestination]
        event_time_to_live: Optional[str]
        max_delivery_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                dead_letter_destination_with_resource_identity: Optional[DeadLetterWithResourceIdentity] = ..., 
                delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity] = ..., 
                destination: Optional[EventSubscriptionDestination] = ..., 
                event_time_to_live: Optional[str] = ..., 
                max_delivery_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.QueueInfo(_Model):
        dead_letter_destination_with_resource_identity: Optional[DeadLetterWithResourceIdentity]
        event_time_to_live: Optional[timedelta]
        max_delivery_count: Optional[int]
        receive_lock_duration_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                dead_letter_destination_with_resource_identity: Optional[DeadLetterWithResourceIdentity] = ..., 
                event_time_to_live: Optional[timedelta] = ..., 
                max_delivery_count: Optional[int] = ..., 
                receive_lock_duration_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ReadinessState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        NEVER_ACTIVATED = "NeverActivated"


    class azure.mgmt.eventgrid.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.eventgrid.models.ResourceAssociation(_Model):
        access_mode: Optional[Union[str, NetworkSecurityPerimeterAssociationAccessMode]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, NetworkSecurityPerimeterAssociationAccessMode]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ResourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        AZURE_ARC = "AzureArc"


    class azure.mgmt.eventgrid.models.ResourceMoveChangeHistory(_Model):
        azure_subscription_id: Optional[str]
        changed_time_utc: Optional[datetime]
        resource_group_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_subscription_id: Optional[str] = ..., 
                changed_time_utc: Optional[datetime] = ..., 
                resource_group_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.ResourceRegionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL_RESOURCE = "GlobalResource"
        REGIONAL_RESOURCE = "RegionalResource"


    class azure.mgmt.eventgrid.models.ResourceSku(_Model):
        name: Optional[Union[str, Sku]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, Sku]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.RetryPolicy(_Model):
        event_time_to_live_in_minutes: Optional[int]
        max_delivery_attempts: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                event_time_to_live_in_minutes: Optional[int] = ..., 
                max_delivery_attempts: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.RoutingEnrichments(_Model):
        dynamic: Optional[list[DynamicRoutingEnrichment]]
        static: Optional[list[StaticRoutingEnrichment]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic: Optional[list[DynamicRoutingEnrichment]] = ..., 
                static: Optional[list[StaticRoutingEnrichment]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.RoutingIdentityInfo(_Model):
        type: Optional[Union[str, RoutingIdentityType]]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, RoutingIdentityType]] = ..., 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.RoutingIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventgrid.models.ServiceBusQueueEventSubscriptionDestination(EventSubscriptionDestination, discriminator='ServiceBusQueue'):
        endpoint_type: Literal[EndpointType.SERVICE_BUS_QUEUE]
        properties: Optional[ServiceBusQueueEventSubscriptionDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceBusQueueEventSubscriptionDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.ServiceBusQueueEventSubscriptionDestinationProperties(_Model):
        delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.ServiceBusTopicEventSubscriptionDestination(EventSubscriptionDestination, discriminator='ServiceBusTopic'):
        endpoint_type: Literal[EndpointType.SERVICE_BUS_TOPIC]
        properties: Optional[ServiceBusTopicEventSubscriptionDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceBusTopicEventSubscriptionDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.ServiceBusTopicEventSubscriptionDestinationProperties(_Model):
        delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.Sku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"


    class azure.mgmt.eventgrid.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD = "Standard"


    class azure.mgmt.eventgrid.models.StaticDeliveryAttributeMapping(DeliveryAttributeMapping, discriminator='Static'):
        name: str
        properties: Optional[StaticDeliveryAttributeMappingProperties]
        type: Literal[DeliveryAttributeMappingType.STATIC]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[StaticDeliveryAttributeMappingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.StaticDeliveryAttributeMappingProperties(_Model):
        is_secret: Optional[bool]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_secret: Optional[bool] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StaticRoutingEnrichment(_Model):
        key: Optional[str]
        value_type: str

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StaticRoutingEnrichmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STRING = "String"


    class azure.mgmt.eventgrid.models.StaticStringRoutingEnrichment(StaticRoutingEnrichment, discriminator='String'):
        key: str
        value: Optional[str]
        value_type: Literal[StaticRoutingEnrichmentType.STRING]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StorageBlobDeadLetterDestination(DeadLetterDestination, discriminator='StorageBlob'):
        endpoint_type: Literal[DeadLetterEndPointType.STORAGE_BLOB]
        properties: Optional[StorageBlobDeadLetterDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageBlobDeadLetterDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.StorageBlobDeadLetterDestinationProperties(_Model):
        blob_container_name: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_container_name: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StorageQueueEventSubscriptionDestination(EventSubscriptionDestination, discriminator='StorageQueue'):
        endpoint_type: Literal[EndpointType.STORAGE_QUEUE]
        properties: Optional[StorageQueueEventSubscriptionDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageQueueEventSubscriptionDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.StorageQueueEventSubscriptionDestinationProperties(_Model):
        queue_message_time_to_live_in_seconds: Optional[int]
        queue_name: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                queue_message_time_to_live_in_seconds: Optional[int] = ..., 
                queue_name: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringBeginsWithAdvancedFilter(AdvancedFilter, discriminator='StringBeginsWith'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.STRING_BEGINS_WITH]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringBeginsWithFilter(Filter, discriminator='StringBeginsWith'):
        key: str
        operator_type: Literal[FilterOperatorType.STRING_BEGINS_WITH]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringContainsAdvancedFilter(AdvancedFilter, discriminator='StringContains'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.STRING_CONTAINS]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringContainsFilter(Filter, discriminator='StringContains'):
        key: str
        operator_type: Literal[FilterOperatorType.STRING_CONTAINS]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringEndsWithAdvancedFilter(AdvancedFilter, discriminator='StringEndsWith'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.STRING_ENDS_WITH]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringEndsWithFilter(Filter, discriminator='StringEndsWith'):
        key: str
        operator_type: Literal[FilterOperatorType.STRING_ENDS_WITH]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringInAdvancedFilter(AdvancedFilter, discriminator='StringIn'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.STRING_IN]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringInFilter(Filter, discriminator='StringIn'):
        key: str
        operator_type: Literal[FilterOperatorType.STRING_IN]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringNotBeginsWithAdvancedFilter(AdvancedFilter, discriminator='StringNotBeginsWith'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.STRING_NOT_BEGINS_WITH]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringNotBeginsWithFilter(Filter, discriminator='StringNotBeginsWith'):
        key: str
        operator_type: Literal[FilterOperatorType.STRING_NOT_BEGINS_WITH]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringNotContainsAdvancedFilter(AdvancedFilter, discriminator='StringNotContains'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.STRING_NOT_CONTAINS]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringNotContainsFilter(Filter, discriminator='StringNotContains'):
        key: str
        operator_type: Literal[FilterOperatorType.STRING_NOT_CONTAINS]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringNotEndsWithAdvancedFilter(AdvancedFilter, discriminator='StringNotEndsWith'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.STRING_NOT_ENDS_WITH]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringNotEndsWithFilter(Filter, discriminator='StringNotEndsWith'):
        key: str
        operator_type: Literal[FilterOperatorType.STRING_NOT_ENDS_WITH]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringNotInAdvancedFilter(AdvancedFilter, discriminator='StringNotIn'):
        key: str
        operator_type: Literal[AdvancedFilterOperatorType.STRING_NOT_IN]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.StringNotInFilter(Filter, discriminator='StringNotIn'):
        key: str
        operator_type: Literal[FilterOperatorType.STRING_NOT_IN]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.Subscription(ProxyResource):
        id: str
        name: str
        properties: Optional[SubscriptionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.SubscriptionFullUrl(_Model):
        endpoint_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.SubscriptionProperties(_Model):
        delivery_configuration: Optional[DeliveryConfiguration]
        event_delivery_schema: Optional[Union[str, DeliverySchema]]
        expiration_time_utc: Optional[datetime]
        filters_configuration: Optional[FiltersConfiguration]
        provisioning_state: Optional[Union[str, SubscriptionProvisioningState]]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                delivery_configuration: Optional[DeliveryConfiguration] = ..., 
                event_delivery_schema: Optional[Union[str, DeliverySchema]] = ..., 
                expiration_time_utc: Optional[datetime] = ..., 
                filters_configuration: Optional[FiltersConfiguration] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.SubscriptionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWAITING_MANUAL_ACTION = "AwaitingManualAction"
        CANCELED = "Canceled"
        CREATE_FAILED = "CreateFailed"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETE_FAILED = "DeleteFailed"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATED_FAILED = "UpdatedFailed"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.SubscriptionUpdateParameters(_Model):
        properties: Optional[SubscriptionUpdateParametersProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionUpdateParametersProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.SubscriptionUpdateParametersProperties(_Model):
        delivery_configuration: Optional[DeliveryConfiguration]
        event_delivery_schema: Optional[Union[str, DeliverySchema]]
        expiration_time_utc: Optional[datetime]
        filters_configuration: Optional[FiltersConfiguration]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                delivery_configuration: Optional[DeliveryConfiguration] = ..., 
                event_delivery_schema: Optional[Union[str, DeliverySchema]] = ..., 
                expiration_time_utc: Optional[datetime] = ..., 
                filters_configuration: Optional[FiltersConfiguration] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.SystemData(_Model):
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


    class azure.mgmt.eventgrid.models.SystemTopic(TrackedResource):
        id: str
        identity: Optional[IdentityInfo]
        location: str
        name: str
        properties: Optional[SystemTopicProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                location: str, 
                properties: Optional[SystemTopicProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.SystemTopicProperties(_Model):
        encryption: Optional[KeyEncryption]
        metric_resource_id: Optional[str]
        platform_capabilities: Optional[PlatformCapabilities]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        source: Optional[str]
        topic_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[KeyEncryption] = ..., 
                platform_capabilities: Optional[PlatformCapabilities] = ..., 
                source: Optional[str] = ..., 
                topic_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.SystemTopicUpdateParameters(_Model):
        identity: Optional[IdentityInfo]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.TlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE0 = "1.0"
        ONE1 = "1.1"
        ONE2 = "1.2"
        ONE3 = "1.3"


    class azure.mgmt.eventgrid.models.Topic(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        identity: Optional[IdentityInfo]
        kind: Optional[Union[str, ResourceKind]]
        location: str
        name: str
        properties: Optional[TopicProperties]
        sku: Optional[ResourceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[IdentityInfo] = ..., 
                kind: Optional[Union[str, ResourceKind]] = ..., 
                location: str, 
                properties: Optional[TopicProperties] = ..., 
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


    class azure.mgmt.eventgrid.models.TopicProperties(_Model):
        data_residency_boundary: Optional[Union[str, DataResidencyBoundary]]
        disable_local_auth: Optional[bool]
        encryption: Optional[KeyEncryption]
        endpoint: Optional[str]
        event_type_info: Optional[EventTypeInfo]
        inbound_ip_rules: Optional[list[InboundIpRule]]
        input_schema: Optional[Union[str, InputSchema]]
        input_schema_mapping: Optional[InputSchemaMapping]
        metric_resource_id: Optional[str]
        minimum_tls_version_allowed: Optional[Union[str, TlsVersion]]
        platform_capabilities: Optional[PlatformCapabilities]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, TopicProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                data_residency_boundary: Optional[Union[str, DataResidencyBoundary]] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[KeyEncryption] = ..., 
                event_type_info: Optional[EventTypeInfo] = ..., 
                inbound_ip_rules: Optional[list[InboundIpRule]] = ..., 
                input_schema: Optional[Union[str, InputSchema]] = ..., 
                input_schema_mapping: Optional[InputSchemaMapping] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                platform_capabilities: Optional[PlatformCapabilities] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.TopicProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.TopicRegenerateKeyRequest(_Model):
        key_name: str

        @overload
        def __init__(
                self, 
                *, 
                key_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.TopicSharedAccessKeys(_Model):
        key1: Optional[str]
        key2: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key1: Optional[str] = ..., 
                key2: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.TopicSpace(ProxyResource):
        id: str
        name: str
        properties: Optional[TopicSpaceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TopicSpaceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.TopicSpaceProperties(_Model):
        description: Optional[str]
        provisioning_state: Optional[Union[str, TopicSpaceProvisioningState]]
        topic_templates: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                topic_templates: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.TopicSpaceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.TopicSpacesConfiguration(_Model):
        client_authentication: Optional[ClientAuthenticationSettings]
        custom_domains: Optional[list[CustomDomainConfiguration]]
        hostname: Optional[str]
        maximum_client_sessions_per_authentication_name: Optional[int]
        maximum_session_expiry_in_hours: Optional[int]
        route_topic_resource_id: Optional[str]
        routing_enrichments: Optional[RoutingEnrichments]
        routing_identity_info: Optional[RoutingIdentityInfo]
        state: Optional[Union[str, TopicSpacesConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                client_authentication: Optional[ClientAuthenticationSettings] = ..., 
                custom_domains: Optional[list[CustomDomainConfiguration]] = ..., 
                maximum_client_sessions_per_authentication_name: Optional[int] = ..., 
                maximum_session_expiry_in_hours: Optional[int] = ..., 
                route_topic_resource_id: Optional[str] = ..., 
                routing_enrichments: Optional[RoutingEnrichments] = ..., 
                routing_identity_info: Optional[RoutingIdentityInfo] = ..., 
                state: Optional[Union[str, TopicSpacesConfigurationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.TopicSpacesConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.eventgrid.models.TopicTypeAdditionalEnforcedPermission(_Model):
        is_data_action: Optional[bool]
        permission_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_data_action: Optional[bool] = ..., 
                permission_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.TopicTypeInfo(ProxyResource):
        id: str
        name: str
        properties: Optional[TopicTypeProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TopicTypeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.TopicTypeProperties(_Model):
        additional_enforced_permissions: Optional[list[TopicTypeAdditionalEnforcedPermission]]
        are_regional_and_global_sources_supported: Optional[bool]
        description: Optional[str]
        display_name: Optional[str]
        provider: Optional[str]
        provisioning_state: Optional[Union[str, TopicTypeProvisioningState]]
        resource_region_type: Optional[Union[str, ResourceRegionType]]
        source_resource_format: Optional[str]
        supported_locations: Optional[list[str]]
        supported_scopes_for_source: Optional[list[Union[str, TopicTypeSourceScope]]]

        @overload
        def __init__(
                self, 
                *, 
                additional_enforced_permissions: Optional[list[TopicTypeAdditionalEnforcedPermission]] = ..., 
                are_regional_and_global_sources_supported: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, TopicTypeProvisioningState]] = ..., 
                resource_region_type: Optional[Union[str, ResourceRegionType]] = ..., 
                source_resource_format: Optional[str] = ..., 
                supported_locations: Optional[list[str]] = ..., 
                supported_scopes_for_source: Optional[list[Union[str, TopicTypeSourceScope]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.TopicTypeProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.TopicTypeSourceScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SUBSCRIPTION = "AzureSubscription"
        MANAGEMENT_GROUP = "ManagementGroup"
        RESOURCE = "Resource"
        RESOURCE_GROUP = "ResourceGroup"


    class azure.mgmt.eventgrid.models.TopicUpdateParameterProperties(_Model):
        data_residency_boundary: Optional[Union[str, DataResidencyBoundary]]
        disable_local_auth: Optional[bool]
        event_type_info: Optional[EventTypeInfo]
        inbound_ip_rules: Optional[list[InboundIpRule]]
        minimum_tls_version_allowed: Optional[Union[str, TlsVersion]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                data_residency_boundary: Optional[Union[str, DataResidencyBoundary]] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                event_type_info: Optional[EventTypeInfo] = ..., 
                inbound_ip_rules: Optional[list[InboundIpRule]] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.TopicUpdateParameters(_Model):
        identity: Optional[IdentityInfo]
        properties: Optional[TopicUpdateParameterProperties]
        sku: Optional[ResourceSku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityInfo] = ..., 
                properties: Optional[TopicUpdateParameterProperties] = ..., 
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


    class azure.mgmt.eventgrid.models.TopicsConfiguration(_Model):
        custom_domains: Optional[list[CustomDomainConfiguration]]
        hostname: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_domains: Optional[list[CustomDomainConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.TrackedResource(Resource):
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


    class azure.mgmt.eventgrid.models.UpdateAutoScaleConfiguration(_Model):
        enable_auto_scale: Optional[bool]
        maximum_throughput_units: Optional[int]
        minimum_throughput_units: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enable_auto_scale: Optional[bool] = ..., 
                maximum_throughput_units: Optional[int] = ..., 
                minimum_throughput_units: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.UpdateTopicSpacesConfigurationInfo(_Model):
        client_authentication: Optional[ClientAuthenticationSettings]
        custom_domains: Optional[list[CustomDomainConfiguration]]
        maximum_client_sessions_per_authentication_name: Optional[int]
        maximum_session_expiry_in_hours: Optional[int]
        route_topic_resource_id: Optional[str]
        routing_enrichments: Optional[RoutingEnrichments]
        routing_identity_info: Optional[RoutingIdentityInfo]
        state: Optional[Union[str, TopicSpacesConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                client_authentication: Optional[ClientAuthenticationSettings] = ..., 
                custom_domains: Optional[list[CustomDomainConfiguration]] = ..., 
                maximum_client_sessions_per_authentication_name: Optional[int] = ..., 
                maximum_session_expiry_in_hours: Optional[int] = ..., 
                route_topic_resource_id: Optional[str] = ..., 
                routing_enrichments: Optional[RoutingEnrichments] = ..., 
                routing_identity_info: Optional[RoutingIdentityInfo] = ..., 
                state: Optional[Union[str, TopicSpacesConfigurationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.UpdateTopicsConfigurationInfo(_Model):
        custom_domains: Optional[list[CustomDomainConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                custom_domains: Optional[list[CustomDomainConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.UserIdentityProperties(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                principal_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.VerifiedPartner(ProxyResource):
        id: str
        name: str
        properties: Optional[VerifiedPartnerProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VerifiedPartnerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.VerifiedPartnerProperties(_Model):
        organization_name: Optional[str]
        partner_destination_details: Optional[PartnerDetails]
        partner_display_name: Optional[str]
        partner_registration_immutable_id: Optional[str]
        partner_topic_details: Optional[PartnerDetails]
        provisioning_state: Optional[Union[str, VerifiedPartnerProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                organization_name: Optional[str] = ..., 
                partner_destination_details: Optional[PartnerDetails] = ..., 
                partner_display_name: Optional[str] = ..., 
                partner_registration_immutable_id: Optional[str] = ..., 
                partner_topic_details: Optional[PartnerDetails] = ..., 
                provisioning_state: Optional[Union[str, VerifiedPartnerProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.VerifiedPartnerProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventgrid.models.WebHookEventSubscriptionDestination(EventSubscriptionDestination, discriminator='WebHook'):
        endpoint_type: Literal[EndpointType.WEB_HOOK]
        properties: Optional[WebHookEventSubscriptionDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WebHookEventSubscriptionDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.WebHookEventSubscriptionDestinationProperties(_Model):
        azure_active_directory_application_id_or_uri: Optional[str]
        azure_active_directory_tenant_id: Optional[str]
        delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]]
        endpoint_base_url: Optional[str]
        endpoint_url: Optional[str]
        max_events_per_batch: Optional[int]
        minimum_tls_version_allowed: Optional[Union[str, TlsVersion]]
        preferred_batch_size_in_kilobytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                azure_active_directory_application_id_or_uri: Optional[str] = ..., 
                azure_active_directory_tenant_id: Optional[str] = ..., 
                delivery_attribute_mappings: Optional[list[DeliveryAttributeMapping]] = ..., 
                endpoint_url: Optional[str] = ..., 
                max_events_per_batch: Optional[int] = ..., 
                minimum_tls_version_allowed: Optional[Union[str, TlsVersion]] = ..., 
                preferred_batch_size_in_kilobytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.WebhookAuthenticationSettings(_Model):
        azure_active_directory_application_id_or_uri: str
        azure_active_directory_tenant_id: str
        endpoint_base_url: Optional[str]
        endpoint_url: str
        identity: CustomWebhookAuthenticationManagedIdentity

        @overload
        def __init__(
                self, 
                *, 
                azure_active_directory_application_id_or_uri: str, 
                azure_active_directory_tenant_id: str, 
                endpoint_base_url: Optional[str] = ..., 
                endpoint_url: str, 
                identity: CustomWebhookAuthenticationManagedIdentity
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.WebhookPartnerDestinationInfo(PartnerDestinationInfo, discriminator='WebHook'):
        azure_subscription_id: str
        endpoint_service_context: str
        endpoint_type: Literal[PartnerEndpointType.WEB_HOOK]
        name: str
        properties: Optional[WebhookPartnerDestinationProperties]
        resource_group_name: str
        resource_move_change_history: list[ResourceMoveChangeHistory]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                azure_subscription_id: Optional[str] = ..., 
                endpoint_service_context: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[WebhookPartnerDestinationProperties] = ..., 
                resource_group_name: Optional[str] = ..., 
                resource_move_change_history: Optional[list[ResourceMoveChangeHistory]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.models.WebhookPartnerDestinationProperties(_Model):
        client_authentication: Optional[PartnerClientAuthentication]
        endpoint_base_url: Optional[str]
        endpoint_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_authentication: Optional[PartnerClientAuthentication] = ..., 
                endpoint_base_url: Optional[str] = ..., 
                endpoint_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventgrid.models.WebhookUpdatePartnerDestinationInfo(PartnerUpdateDestinationInfo, discriminator='WebHook'):
        endpoint_type: Literal[PartnerEndpointType.WEB_HOOK]
        properties: Optional[WebhookPartnerDestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WebhookPartnerDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


namespace azure.mgmt.eventgrid.operations

    class azure.mgmt.eventgrid.operations.CaCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                ca_certificate_info: CaCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CaCertificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                ca_certificate_info: CaCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CaCertificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                ca_certificate_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CaCertificate]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                ca_certificate_name: str, 
                **kwargs: Any
            ) -> CaCertificate: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CaCertificate]: ...


    class azure.mgmt.eventgrid.operations.ChannelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_info: Channel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Channel: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_info: Channel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Channel: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Channel: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> Channel: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_partner_namespace(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Channel]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_update_parameters: ChannelUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_update_parameters: ChannelUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                channel_name: str, 
                channel_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.eventgrid.operations.ClientGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                client_group_info: ClientGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClientGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                client_group_info: ClientGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClientGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                client_group_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClientGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_group_name: str, 
                **kwargs: Any
            ) -> ClientGroup: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ClientGroup]: ...


    class azure.mgmt.eventgrid.operations.ClientsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                client_info: Client, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Client]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                client_info: Client, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Client]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                client_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Client]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                client_name: str, 
                **kwargs: Any
            ) -> Client: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Client]: ...


    class azure.mgmt.eventgrid.operations.DomainEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.DomainTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.DomainTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[DomainTopic]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_topic_name: str, 
                **kwargs: Any
            ) -> DomainTopic: ...

        @distributed_trace
        def list_by_domain(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DomainTopic]: ...


    class azure.mgmt.eventgrid.operations.DomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_info: Domain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_info: Domain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_update_parameters: DomainUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_update_parameters: DomainUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> Domain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Domain]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Domain]: ...

        @distributed_trace
        def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                regenerate_key_request: DomainRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                regenerate_key_request: DomainRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainSharedAccessKeys: ...


    class azure.mgmt.eventgrid.operations.EventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                scope: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                scope: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_domain_topic(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                provider_namespace: str, 
                resource_type_name: str, 
                resource_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_resource_group_for_topic_type(
                self, 
                resource_group_name: str, 
                topic_type_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_global_by_subscription_for_topic_type(
                self, 
                topic_type_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_resource_group_for_topic_type(
                self, 
                resource_group_name: str, 
                location: str, 
                topic_type_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_subscription(
                self, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...

        @distributed_trace
        def list_regional_by_subscription_for_topic_type(
                self, 
                location: str, 
                topic_type_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.ExtensionTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ExtensionTopic: ...


    class azure.mgmt.eventgrid.operations.NamespaceTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: Subscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Subscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: Subscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Subscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Subscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: SubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Subscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: SubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Subscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Subscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> Subscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> SubscriptionFullUrl: ...

        @distributed_trace
        def list_by_namespace_topic(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Subscription]: ...


    class azure.mgmt.eventgrid.operations.NamespaceTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_info: NamespaceTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceTopic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_info: NamespaceTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceTopic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceTopic]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSharedAccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSharedAccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSharedAccessKeys]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_update_parameters: NamespaceTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceTopic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_update_parameters: NamespaceTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceTopic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                namespace_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceTopic]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> NamespaceTopic: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NamespaceTopic]: ...

        @distributed_trace
        def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicSharedAccessKeys: ...


    class azure.mgmt.eventgrid.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_info: Namespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_info: Namespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                regenerate_key_request: NamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceSharedAccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                regenerate_key_request: NamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceSharedAccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceSharedAccessKeys]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_update_parameters: NamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_update_parameters: NamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                namespace_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @distributed_trace
        def begin_validate_custom_domain_ownership(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[CustomDomainOwnershipValidationResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Namespace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Namespace]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Namespace]: ...

        @distributed_trace
        def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NamespaceSharedAccessKeys: ...


    class azure.mgmt.eventgrid.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_reconcile(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                perimeter_guid: str, 
                association_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityPerimeterConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                perimeter_guid: str, 
                association_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_type: Union[str, NetworkSecurityPerimeterResourceType], 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.eventgrid.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.eventgrid.operations.PartnerConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def authorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        def authorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        def authorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_configuration_info: PartnerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_configuration_info: PartnerConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_configuration_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerConfiguration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_configuration_update_parameters: PartnerConfigurationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_configuration_update_parameters: PartnerConfigurationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_configuration_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PartnerConfiguration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PartnerConfiguration]: ...

        @overload
        def unauthorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        def unauthorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: Partner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...

        @overload
        def unauthorize_partner(
                self, 
                resource_group_name: str, 
                partner_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerConfiguration: ...


    class azure.mgmt.eventgrid.operations.PartnerDestinationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def activate(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> PartnerDestination: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination: PartnerDestination, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerDestination]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination: PartnerDestination, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerDestination]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerDestination]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination_update_parameters: PartnerDestinationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerDestination]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination_update_parameters: PartnerDestinationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerDestination]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                partner_destination_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerDestination]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_destination_name: str, 
                **kwargs: Any
            ) -> PartnerDestination: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PartnerDestination]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PartnerDestination]: ...


    class azure.mgmt.eventgrid.operations.PartnerNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_info: PartnerNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_info: PartnerNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerNamespace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_update_parameters: PartnerNamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerNamespace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_update_parameters: PartnerNamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerNamespace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                partner_namespace_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerNamespace]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> PartnerNamespace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PartnerNamespace]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PartnerNamespace]: ...

        @distributed_trace
        def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                regenerate_key_request: PartnerNamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                regenerate_key_request: PartnerNamespaceRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                partner_namespace_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerNamespaceSharedAccessKeys: ...


    class azure.mgmt.eventgrid.operations.PartnerRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_info: PartnerRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerRegistration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_info: PartnerRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerRegistration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerRegistration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_update_parameters: PartnerRegistrationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerRegistration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_update_parameters: PartnerRegistrationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerRegistration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                partner_registration_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PartnerRegistration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_registration_name: str, 
                **kwargs: Any
            ) -> PartnerRegistration: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PartnerRegistration]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PartnerRegistration]: ...


    class azure.mgmt.eventgrid.operations.PartnerTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_partner_topic(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.PartnerTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def activate(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_info: PartnerTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_info: PartnerTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace
        def deactivate(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                **kwargs: Any
            ) -> PartnerTopic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PartnerTopic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PartnerTopic]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_update_parameters: PartnerTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[PartnerTopic]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_update_parameters: PartnerTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[PartnerTopic]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                partner_topic_name: str, 
                partner_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[PartnerTopic]: ...


    class azure.mgmt.eventgrid.operations.PermissionBindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                permission_binding_info: PermissionBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PermissionBinding]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                permission_binding_info: PermissionBinding, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PermissionBinding]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                permission_binding_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PermissionBinding]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                permission_binding_name: str, 
                **kwargs: Any
            ) -> PermissionBinding: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PermissionBinding]: ...


    class azure.mgmt.eventgrid.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
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
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
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
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
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
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                parent_type: Union[str, PrivateEndpointConnectionsParentType], 
                parent_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.eventgrid.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                parent_type: str, 
                parent_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                parent_type: str, 
                parent_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.eventgrid.operations.SystemTopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list_by_system_topic(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.SystemTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_info: SystemTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SystemTopic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_info: SystemTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SystemTopic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SystemTopic]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_update_parameters: SystemTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SystemTopic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_update_parameters: SystemTopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SystemTopic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                system_topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SystemTopic]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                system_topic_name: str, 
                **kwargs: Any
            ) -> SystemTopic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SystemTopic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SystemTopic]: ...


    class azure.mgmt.eventgrid.operations.TopicEventSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: EventSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: EventSubscriptionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                event_subscription_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EventSubscription]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscription: ...

        @distributed_trace
        def get_delivery_attributes(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> DeliveryAttributeListResult: ...

        @distributed_trace
        def get_full_url(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                event_subscription_name: str, 
                **kwargs: Any
            ) -> EventSubscriptionFullUrl: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSubscription]: ...


    class azure.mgmt.eventgrid.operations.TopicSpacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                topic_space_info: TopicSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSpace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                topic_space_info: TopicSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSpace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                topic_space_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSpace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_space_name: str, 
                **kwargs: Any
            ) -> TopicSpace: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TopicSpace]: ...


    class azure.mgmt.eventgrid.operations.TopicTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                topic_type_name: str, 
                **kwargs: Any
            ) -> TopicTypeInfo: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[TopicTypeInfo]: ...

        @distributed_trace
        def list_event_types(
                self, 
                topic_type_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EventType]: ...


    class azure.mgmt.eventgrid.operations.TopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_info: Topic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Topic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_info: Topic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Topic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Topic]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSharedAccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                regenerate_key_request: TopicRegenerateKeyRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSharedAccessKeys]: ...

        @overload
        def begin_regenerate_key(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                regenerate_key_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TopicSharedAccessKeys]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_update_parameters: TopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Topic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_update_parameters: TopicUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Topic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                topic_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Topic]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> Topic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Topic]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Topic]: ...

        @distributed_trace
        def list_event_types(
                self, 
                resource_group_name: str, 
                provider_namespace: str, 
                resource_type_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EventType]: ...

        @distributed_trace
        def list_shared_access_keys(
                self, 
                resource_group_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicSharedAccessKeys: ...


    class azure.mgmt.eventgrid.operations.VerifiedPartnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                verified_partner_name: str, 
                **kwargs: Any
            ) -> VerifiedPartner: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VerifiedPartner]: ...


namespace azure.mgmt.eventgrid.types

    class azure.mgmt.eventgrid.types.AdvancedFilterOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL_EQUALS = "BoolEquals"
        IS_NOT_NULL = "IsNotNull"
        IS_NULL_OR_UNDEFINED = "IsNullOrUndefined"
        NUMBER_GREATER_THAN = "NumberGreaterThan"
        NUMBER_GREATER_THAN_OR_EQUALS = "NumberGreaterThanOrEquals"
        NUMBER_IN = "NumberIn"
        NUMBER_IN_RANGE = "NumberInRange"
        NUMBER_LESS_THAN = "NumberLessThan"
        NUMBER_LESS_THAN_OR_EQUALS = "NumberLessThanOrEquals"
        NUMBER_NOT_IN = "NumberNotIn"
        NUMBER_NOT_IN_RANGE = "NumberNotInRange"
        STRING_BEGINS_WITH = "StringBeginsWith"
        STRING_CONTAINS = "StringContains"
        STRING_ENDS_WITH = "StringEndsWith"
        STRING_IN = "StringIn"
        STRING_NOT_BEGINS_WITH = "StringNotBeginsWith"
        STRING_NOT_CONTAINS = "StringNotContains"
        STRING_NOT_ENDS_WITH = "StringNotEndsWith"
        STRING_NOT_IN = "StringNotIn"


    class azure.mgmt.eventgrid.types.AutoScaleConfiguration(TypedDict, total=False):
        key "enableAutoScale": bool
        key "maximumThroughputUnits": int
        key "minimumThroughputUnits": int
        enableAutoScale: bool
        maximumThroughputUnits: int
        minimumThroughputUnits: int


    class azure.mgmt.eventgrid.types.AzureADPartnerClientAuthentication(TypedDict, total=False):
        key "clientAuthenticationType": Required[Literal[PartnerClientAuthenticationType.AZURE_AD]]
        key "properties": ForwardRef('AzureADPartnerClientAuthenticationProperties', module='types')
        clientAuthenticationType: Literal[PartnerClientAuthenticationType.AZURE_AD]
        properties: AzureADPartnerClientAuthenticationProperties


    class azure.mgmt.eventgrid.types.AzureADPartnerClientAuthenticationProperties(TypedDict, total=False):
        key "azureActiveDirectoryApplicationIdOrUri": str
        key "azureActiveDirectoryTenantId": str
        azureActiveDirectoryApplicationIdOrUri: str
        azureActiveDirectoryTenantId: str


    class azure.mgmt.eventgrid.types.AzureFunctionEventSubscriptionDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[EndpointType.AZURE_FUNCTION]]
        key "properties": ForwardRef('AzureFunctionEventSubscriptionDestinationProperties', module='types')
        endpointType: Literal[EndpointType.AZURE_FUNCTION]
        properties: AzureFunctionEventSubscriptionDestinationProperties


    class azure.mgmt.eventgrid.types.AzureFunctionEventSubscriptionDestinationProperties(TypedDict, total=False):
        key "maxEventsPerBatch": int
        key "preferredBatchSizeInKilobytes": int
        key "resourceId": str
        deliveryAttributeMappings: list[DeliveryAttributeMapping]
        maxEventsPerBatch: int
        preferredBatchSizeInKilobytes: int
        resourceId: str


    class azure.mgmt.eventgrid.types.BoolEqualsAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.BOOL_EQUALS]]
        key "value": bool
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.BOOL_EQUALS]
        value: bool


    class azure.mgmt.eventgrid.types.BoolEqualsFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.BOOL_EQUALS]]
        key "value": bool
        key: str
        operatorType: Literal[FilterOperatorType.BOOL_EQUALS]
        value: bool


    class azure.mgmt.eventgrid.types.CaCertificate(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('CaCertificateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CaCertificateProperties
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.CaCertificateProperties(TypedDict, total=False):
        key "description": str
        key "encodedCertificate": str
        key "expiryTimeInUtc": str
        key "issueTimeInUtc": str
        key "provisioningState": Union[str, CaCertificateProvisioningState]
        description: str
        encodedCertificate: str
        expiryTimeInUtc: str
        issueTimeInUtc: str
        provisioningState: Union[str, CaCertificateProvisioningState]


    class azure.mgmt.eventgrid.types.Channel(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ChannelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ChannelProperties
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.ChannelProperties(TypedDict, total=False):
        key "channelType": Union[str, ChannelType]
        key "expirationTimeIfNotActivatedUtc": str
        key "messageForActivation": str
        key "partnerDestinationInfo": ForwardRef('PartnerDestinationInfo', module='types')
        key "partnerTopicInfo": ForwardRef('PartnerTopicInfo', module='types')
        key "provisioningState": Union[str, ChannelProvisioningState]
        key "readinessState": Union[str, ReadinessState]
        channelType: Union[str, ChannelType]
        expirationTimeIfNotActivatedUtc: str
        messageForActivation: str
        partnerDestinationInfo: PartnerDestinationInfo
        partnerTopicInfo: PartnerTopicInfo
        provisioningState: Union[str, ChannelProvisioningState]
        readinessState: Union[str, ReadinessState]


    class azure.mgmt.eventgrid.types.ChannelUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('ChannelUpdateParametersProperties', module='types')
        properties: ChannelUpdateParametersProperties


    class azure.mgmt.eventgrid.types.ChannelUpdateParametersProperties(TypedDict, total=False):
        key "expirationTimeIfNotActivatedUtc": str
        key "partnerDestinationInfo": ForwardRef('PartnerUpdateDestinationInfo', module='types')
        key "partnerTopicInfo": ForwardRef('PartnerUpdateTopicInfo', module='types')
        expirationTimeIfNotActivatedUtc: str
        partnerDestinationInfo: PartnerUpdateDestinationInfo
        partnerTopicInfo: PartnerUpdateTopicInfo


    class azure.mgmt.eventgrid.types.Client(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ClientProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ClientProperties
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.ClientAuthenticationSettings(TypedDict, total=False):
        key "customJwtAuthentication": ForwardRef('CustomJwtAuthenticationSettings', module='types')
        key "webhookAuthentication": ForwardRef('WebhookAuthenticationSettings', module='types')
        alternativeAuthenticationNameSources: list[Union[str, AlternativeAuthenticationNameSource]]
        customJwtAuthentication: CustomJwtAuthenticationSettings
        webhookAuthentication: WebhookAuthenticationSettings


    class azure.mgmt.eventgrid.types.ClientCertificateAuthentication(TypedDict, total=False):
        key "validationScheme": Union[str, ClientCertificateValidationScheme]
        allowedThumbprints: list[str]
        validationScheme: Union[str, ClientCertificateValidationScheme]


    class azure.mgmt.eventgrid.types.ClientGroup(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ClientGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ClientGroupProperties
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.ClientGroupProperties(TypedDict, total=False):
        key "description": str
        key "provisioningState": Union[str, ClientGroupProvisioningState]
        key "query": str
        description: str
        provisioningState: Union[str, ClientGroupProvisioningState]
        query: str


    class azure.mgmt.eventgrid.types.ClientProperties(TypedDict, total=False):
        key "authenticationName": str
        key "clientCertificateAuthentication": ForwardRef('ClientCertificateAuthentication', module='types')
        key "description": str
        key "provisioningState": Union[str, ClientProvisioningState]
        key "state": Union[str, ClientState]
        attributes: dict[str, Any]
        authenticationName: str
        clientCertificateAuthentication: ClientCertificateAuthentication
        description: str
        provisioningState: Union[str, ClientProvisioningState]
        state: Union[str, ClientState]


    class azure.mgmt.eventgrid.types.ConfidentialCompute(TypedDict, total=False):
        key "mode": Required[Union[str, ConfidentialComputeMode]]
        mode: Union[str, ConfidentialComputeMode]


    class azure.mgmt.eventgrid.types.ConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PersistedConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PersistedConnectionStatus]


    class azure.mgmt.eventgrid.types.CustomDomainConfiguration(TypedDict, total=False):
        key "certificateUrl": str
        key "expectedTxtRecordName": str
        key "expectedTxtRecordValue": str
        key "fullyQualifiedDomainName": Required[str]
        key "identity": ForwardRef('CustomDomainIdentity', module='types')
        key "validationState": Union[str, CustomDomainValidationState]
        certificateUrl: str
        expectedTxtRecordName: str
        expectedTxtRecordValue: str
        fullyQualifiedDomainName: str
        identity: CustomDomainIdentity
        validationState: Union[str, CustomDomainValidationState]


    class azure.mgmt.eventgrid.types.CustomDomainIdentity(TypedDict, total=False):
        key "type": Union[str, CustomDomainIdentityType]
        key "userAssignedIdentity": str
        type: Union[str, CustomDomainIdentityType]
        userAssignedIdentity: str


    class azure.mgmt.eventgrid.types.CustomJwtAuthenticationManagedIdentity(TypedDict, total=False):
        key "type": Required[Union[str, CustomJwtAuthenticationManagedIdentityType]]
        key "userAssignedIdentity": str
        type: Union[str, CustomJwtAuthenticationManagedIdentityType]
        userAssignedIdentity: str


    class azure.mgmt.eventgrid.types.CustomJwtAuthenticationSettings(TypedDict, total=False):
        key "tokenIssuer": str
        encodedIssuerCertificates: list[EncodedIssuerCertificateInfo]
        issuerCertificates: list[IssuerCertificateInfo]
        tokenIssuer: str


    class azure.mgmt.eventgrid.types.CustomWebhookAuthenticationManagedIdentity(TypedDict, total=False):
        key "type": Required[Union[str, CustomWebhookAuthenticationManagedIdentityType]]
        key "userAssignedIdentity": str
        type: Union[str, CustomWebhookAuthenticationManagedIdentityType]
        userAssignedIdentity: str


    class azure.mgmt.eventgrid.types.CustomerManagedKeyEncryption(TypedDict, total=False):
        key "keyEncryptionKeyIdentity": ForwardRef('KeyEncryptionKeyIdentity', module='types')
        key "keyEncryptionKeyStatus": Union[str, KeyEncryptionKeyStatus]
        key "keyEncryptionKeyStatusFriendlyDescription": str
        key "keyEncryptionKeyUrl": Required[str]
        keyEncryptionKeyIdentity: KeyEncryptionKeyIdentity
        keyEncryptionKeyStatus: Union[str, KeyEncryptionKeyStatus]
        keyEncryptionKeyStatusFriendlyDescription: str
        keyEncryptionKeyUrl: str


    class azure.mgmt.eventgrid.types.DeadLetterDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[DeadLetterEndPointType.STORAGE_BLOB]]
        key "properties": ForwardRef('StorageBlobDeadLetterDestinationProperties', module='types')
        endpointType: Literal[DeadLetterEndPointType.STORAGE_BLOB]
        properties: StorageBlobDeadLetterDestinationProperties


    class azure.mgmt.eventgrid.types.DeadLetterEndPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STORAGE_BLOB = "StorageBlob"


    class azure.mgmt.eventgrid.types.DeadLetterWithResourceIdentity(TypedDict, total=False):
        key "deadLetterDestination": ForwardRef('DeadLetterDestination', module='types')
        key "identity": ForwardRef('EventSubscriptionIdentity', module='types')
        deadLetterDestination: DeadLetterDestination
        identity: EventSubscriptionIdentity


    class azure.mgmt.eventgrid.types.DeliveryAttributeMappingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.eventgrid.types.DeliveryConfiguration(TypedDict, total=False):
        key "deliveryMode": Union[str, DeliveryMode]
        key "push": ForwardRef('PushInfo', module='types')
        key "queue": ForwardRef('QueueInfo', module='types')
        deliveryMode: Union[str, DeliveryMode]
        push: PushInfo
        queue: QueueInfo


    class azure.mgmt.eventgrid.types.DeliveryWithResourceIdentity(TypedDict, total=False):
        key "destination": ForwardRef('EventSubscriptionDestination', module='types')
        key "identity": ForwardRef('EventSubscriptionIdentity', module='types')
        destination: EventSubscriptionDestination
        identity: EventSubscriptionIdentity


    class azure.mgmt.eventgrid.types.Domain(TrackedResource):
        key "id": str
        key "identity": ForwardRef('IdentityInfo', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DomainProperties', module='types')
        key "sku": ForwardRef('ResourceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityInfo
        location: str
        name: str
        properties: DomainProperties
        sku: ResourceSku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventgrid.types.DomainProperties(TypedDict, total=False):
        key "autoCreateTopicWithFirstSubscription": bool
        key "autoDeleteTopicWithLastSubscription": bool
        key "dataResidencyBoundary": Union[str, DataResidencyBoundary]
        key "disableLocalAuth": bool
        key "endpoint": str
        key "eventTypeInfo": ForwardRef('EventTypeInfo', module='types')
        key "inputSchema": Union[str, InputSchema]
        key "inputSchemaMapping": ForwardRef('InputSchemaMapping', module='types')
        key "metricResourceId": str
        key "minimumTlsVersionAllowed": Union[str, TlsVersion]
        key "provisioningState": Union[str, DomainProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        autoCreateTopicWithFirstSubscription: bool
        autoDeleteTopicWithLastSubscription: bool
        dataResidencyBoundary: Union[str, DataResidencyBoundary]
        disableLocalAuth: bool
        endpoint: str
        eventTypeInfo: EventTypeInfo
        inboundIpRules: list[InboundIpRule]
        inputSchema: Union[str, InputSchema]
        inputSchemaMapping: InputSchemaMapping
        metricResourceId: str
        minimumTlsVersionAllowed: Union[str, TlsVersion]
        privateEndpointConnections: list[PrivateEndpointConnection]
        provisioningState: Union[str, DomainProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]


    class azure.mgmt.eventgrid.types.DomainRegenerateKeyRequest(TypedDict, total=False):
        key "keyName": Required[str]
        keyName: str


    class azure.mgmt.eventgrid.types.DomainUpdateParameterProperties(TypedDict, total=False):
        key "autoCreateTopicWithFirstSubscription": bool
        key "autoDeleteTopicWithLastSubscription": bool
        key "dataResidencyBoundary": Union[str, DataResidencyBoundary]
        key "disableLocalAuth": bool
        key "eventTypeInfo": ForwardRef('EventTypeInfo', module='types')
        key "minimumTlsVersionAllowed": Union[str, TlsVersion]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        autoCreateTopicWithFirstSubscription: bool
        autoDeleteTopicWithLastSubscription: bool
        dataResidencyBoundary: Union[str, DataResidencyBoundary]
        disableLocalAuth: bool
        eventTypeInfo: EventTypeInfo
        inboundIpRules: list[InboundIpRule]
        minimumTlsVersionAllowed: Union[str, TlsVersion]
        publicNetworkAccess: Union[str, PublicNetworkAccess]


    class azure.mgmt.eventgrid.types.DomainUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('IdentityInfo', module='types')
        key "properties": ForwardRef('DomainUpdateParameterProperties', module='types')
        key "sku": ForwardRef('ResourceSku', module='types')
        identity: IdentityInfo
        properties: DomainUpdateParameterProperties
        sku: ResourceSku
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.DynamicDeliveryAttributeMapping(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('DynamicDeliveryAttributeMappingProperties', module='types')
        key "type": Required[Literal[DeliveryAttributeMappingType.DYNAMIC]]
        name: str
        properties: DynamicDeliveryAttributeMappingProperties
        type: Literal[DeliveryAttributeMappingType.DYNAMIC]


    class azure.mgmt.eventgrid.types.DynamicDeliveryAttributeMappingProperties(TypedDict, total=False):
        key "sourceField": str
        sourceField: str


    class azure.mgmt.eventgrid.types.DynamicRoutingEnrichment(TypedDict, total=False):
        key "key": str
        key "value": str
        key: str
        value: str


    class azure.mgmt.eventgrid.types.EncodedIssuerCertificateInfo(TypedDict, total=False):
        key "encodedCertificate": Required[str]
        key "kid": Required[str]
        encodedCertificate: str
        kid: str


    class azure.mgmt.eventgrid.types.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FUNCTION = "AzureFunction"
        EVENT_HUB = "EventHub"
        HYBRID_CONNECTION = "HybridConnection"
        MONITOR_ALERT = "MonitorAlert"
        NAMESPACE_TOPIC = "NamespaceTopic"
        PARTNER_DESTINATION = "PartnerDestination"
        SERVICE_BUS_QUEUE = "ServiceBusQueue"
        SERVICE_BUS_TOPIC = "ServiceBusTopic"
        STORAGE_QUEUE = "StorageQueue"
        WEB_HOOK = "WebHook"


    class azure.mgmt.eventgrid.types.EventHubEventSubscriptionDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[EndpointType.EVENT_HUB]]
        key "properties": ForwardRef('EventHubEventSubscriptionDestinationProperties', module='types')
        endpointType: Literal[EndpointType.EVENT_HUB]
        properties: EventHubEventSubscriptionDestinationProperties


    class azure.mgmt.eventgrid.types.EventHubEventSubscriptionDestinationProperties(TypedDict, total=False):
        key "resourceId": str
        deliveryAttributeMappings: list[DeliveryAttributeMapping]
        resourceId: str


    class azure.mgmt.eventgrid.types.EventSubscription(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EventSubscriptionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EventSubscriptionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.EventSubscriptionFilter(TypedDict, total=False):
        key "enableAdvancedFilteringOnArrays": bool
        key "isSubjectCaseSensitive": bool
        key "subjectBeginsWith": str
        key "subjectEndsWith": str
        advancedFilters: list[AdvancedFilter]
        enableAdvancedFilteringOnArrays: bool
        includedEventTypes: list[str]
        isSubjectCaseSensitive: bool
        subjectBeginsWith: str
        subjectEndsWith: str


    class azure.mgmt.eventgrid.types.EventSubscriptionIdentity(TypedDict, total=False):
        key "federatedIdentityCredentialInfo": ForwardRef('FederatedIdentityCredentialInfo', module='types')
        key "type": Union[str, EventSubscriptionIdentityType]
        key "userAssignedIdentity": str
        federatedIdentityCredentialInfo: FederatedIdentityCredentialInfo
        type: Union[str, EventSubscriptionIdentityType]
        userAssignedIdentity: str


    class azure.mgmt.eventgrid.types.EventSubscriptionProperties(TypedDict, total=False):
        key "deadLetterDestination": ForwardRef('DeadLetterDestination', module='types')
        key "deadLetterWithResourceIdentity": ForwardRef('DeadLetterWithResourceIdentity', module='types')
        key "deliveryWithResourceIdentity": ForwardRef('DeliveryWithResourceIdentity', module='types')
        key "destination": ForwardRef('EventSubscriptionDestination', module='types')
        key "eventDeliverySchema": Union[str, EventDeliverySchema]
        key "expirationTimeUtc": str
        key "filter": ForwardRef('EventSubscriptionFilter', module='types')
        key "provisioningState": Union[str, EventSubscriptionProvisioningState]
        key "retryPolicy": ForwardRef('RetryPolicy', module='types')
        key "topic": str
        deadLetterDestination: DeadLetterDestination
        deadLetterWithResourceIdentity: DeadLetterWithResourceIdentity
        deliveryWithResourceIdentity: DeliveryWithResourceIdentity
        destination: EventSubscriptionDestination
        eventDeliverySchema: Union[str, EventDeliverySchema]
        expirationTimeUtc: str
        filter: EventSubscriptionFilter
        labels: list[str]
        provisioningState: Union[str, EventSubscriptionProvisioningState]
        retryPolicy: RetryPolicy
        topic: str


    class azure.mgmt.eventgrid.types.EventSubscriptionUpdateParameters(TypedDict, total=False):
        key "deadLetterDestination": ForwardRef('DeadLetterDestination', module='types')
        key "deadLetterWithResourceIdentity": ForwardRef('DeadLetterWithResourceIdentity', module='types')
        key "deliveryWithResourceIdentity": ForwardRef('DeliveryWithResourceIdentity', module='types')
        key "destination": ForwardRef('EventSubscriptionDestination', module='types')
        key "eventDeliverySchema": Union[str, EventDeliverySchema]
        key "expirationTimeUtc": str
        key "filter": ForwardRef('EventSubscriptionFilter', module='types')
        key "retryPolicy": ForwardRef('RetryPolicy', module='types')
        deadLetterDestination: DeadLetterDestination
        deadLetterWithResourceIdentity: DeadLetterWithResourceIdentity
        deliveryWithResourceIdentity: DeliveryWithResourceIdentity
        destination: EventSubscriptionDestination
        eventDeliverySchema: Union[str, EventDeliverySchema]
        expirationTimeUtc: str
        filter: EventSubscriptionFilter
        labels: list[str]
        retryPolicy: RetryPolicy


    class azure.mgmt.eventgrid.types.EventTypeInfo(TypedDict, total=False):
        key "kind": Union[str, EventDefinitionKind]
        inlineEventTypes: dict[str, InlineEventProperties]
        kind: Union[str, EventDefinitionKind]


    class azure.mgmt.eventgrid.types.ExtendedLocation(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.eventgrid.types.FederatedIdentityCredentialInfo(TypedDict, total=False):
        key "federatedClientId": Required[str]
        federatedClientId: str


    class azure.mgmt.eventgrid.types.FilterOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL_EQUALS = "BoolEquals"
        IS_NOT_NULL = "IsNotNull"
        IS_NULL_OR_UNDEFINED = "IsNullOrUndefined"
        NUMBER_GREATER_THAN = "NumberGreaterThan"
        NUMBER_GREATER_THAN_OR_EQUALS = "NumberGreaterThanOrEquals"
        NUMBER_IN = "NumberIn"
        NUMBER_IN_RANGE = "NumberInRange"
        NUMBER_LESS_THAN = "NumberLessThan"
        NUMBER_LESS_THAN_OR_EQUALS = "NumberLessThanOrEquals"
        NUMBER_NOT_IN = "NumberNotIn"
        NUMBER_NOT_IN_RANGE = "NumberNotInRange"
        STRING_BEGINS_WITH = "StringBeginsWith"
        STRING_CONTAINS = "StringContains"
        STRING_ENDS_WITH = "StringEndsWith"
        STRING_IN = "StringIn"
        STRING_NOT_BEGINS_WITH = "StringNotBeginsWith"
        STRING_NOT_CONTAINS = "StringNotContains"
        STRING_NOT_ENDS_WITH = "StringNotEndsWith"
        STRING_NOT_IN = "StringNotIn"


    class azure.mgmt.eventgrid.types.FiltersConfiguration(TypedDict, total=False):
        filters: list[Filter]
        includedEventTypes: list[str]


    class azure.mgmt.eventgrid.types.HybridConnectionEventSubscriptionDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[EndpointType.HYBRID_CONNECTION]]
        key "properties": ForwardRef('HybridConnectionEventSubscriptionDestinationProperties', module='types')
        endpointType: Literal[EndpointType.HYBRID_CONNECTION]
        properties: HybridConnectionEventSubscriptionDestinationProperties


    class azure.mgmt.eventgrid.types.HybridConnectionEventSubscriptionDestinationProperties(TypedDict, total=False):
        key "resourceId": str
        deliveryAttributeMappings: list[DeliveryAttributeMapping]
        resourceId: str


    class azure.mgmt.eventgrid.types.IdentityInfo(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, IdentityType]
        principalId: str
        tenantId: str
        type: Union[str, IdentityType]
        userAssignedIdentities: dict[str, UserIdentityProperties]


    class azure.mgmt.eventgrid.types.InboundIpRule(TypedDict, total=False):
        key "action": Union[str, IpActionType]
        key "ipMask": str
        action: Union[str, IpActionType]
        ipMask: str


    class azure.mgmt.eventgrid.types.InlineEventProperties(TypedDict, total=False):
        key "dataSchemaUrl": str
        key "description": str
        key "displayName": str
        key "documentationUrl": str
        dataSchemaUrl: str
        description: str
        displayName: str
        documentationUrl: str


    class azure.mgmt.eventgrid.types.InputSchemaMapping(TypedDict, total=False):
        key "inputSchemaMappingType": Required[Literal[InputSchemaMappingType.JSON]]
        key "properties": ForwardRef('JsonInputSchemaMappingProperties', module='types')
        inputSchemaMappingType: Literal[InputSchemaMappingType.JSON]
        properties: JsonInputSchemaMappingProperties


    class azure.mgmt.eventgrid.types.InputSchemaMappingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "Json"


    class azure.mgmt.eventgrid.types.IsNotNullAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.IS_NOT_NULL]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.IS_NOT_NULL]


    class azure.mgmt.eventgrid.types.IsNotNullFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.IS_NOT_NULL]]
        key: str
        operatorType: Literal[FilterOperatorType.IS_NOT_NULL]


    class azure.mgmt.eventgrid.types.IsNullOrUndefinedAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.IS_NULL_OR_UNDEFINED]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.IS_NULL_OR_UNDEFINED]


    class azure.mgmt.eventgrid.types.IsNullOrUndefinedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.IS_NULL_OR_UNDEFINED]]
        key: str
        operatorType: Literal[FilterOperatorType.IS_NULL_OR_UNDEFINED]


    class azure.mgmt.eventgrid.types.IssuerCertificateInfo(TypedDict, total=False):
        key "certificateUrl": Required[str]
        key "identity": ForwardRef('CustomJwtAuthenticationManagedIdentity', module='types')
        certificateUrl: str
        identity: CustomJwtAuthenticationManagedIdentity


    class azure.mgmt.eventgrid.types.JsonField(TypedDict, total=False):
        key "sourceField": str
        sourceField: str


    class azure.mgmt.eventgrid.types.JsonFieldWithDefault(TypedDict, total=False):
        key "defaultValue": str
        key "sourceField": str
        defaultValue: str
        sourceField: str


    class azure.mgmt.eventgrid.types.JsonInputSchemaMapping(TypedDict, total=False):
        key "inputSchemaMappingType": Required[Literal[InputSchemaMappingType.JSON]]
        key "properties": ForwardRef('JsonInputSchemaMappingProperties', module='types')
        inputSchemaMappingType: Literal[InputSchemaMappingType.JSON]
        properties: JsonInputSchemaMappingProperties


    class azure.mgmt.eventgrid.types.JsonInputSchemaMappingProperties(TypedDict, total=False):
        key "dataVersion": ForwardRef('JsonFieldWithDefault', module='types')
        key "eventTime": ForwardRef('JsonField', module='types')
        key "eventType": ForwardRef('JsonFieldWithDefault', module='types')
        key "id": ForwardRef('JsonField', module='types')
        key "subject": ForwardRef('JsonFieldWithDefault', module='types')
        key "topic": ForwardRef('JsonField', module='types')
        dataVersion: JsonFieldWithDefault
        eventTime: JsonField
        eventType: JsonFieldWithDefault
        id: JsonField
        subject: JsonFieldWithDefault
        topic: JsonField


    class azure.mgmt.eventgrid.types.KeyEncryption(TypedDict, total=False):
        key "customerManagedKeyEncryption": Required[list[CustomerManagedKeyEncryption]]
        customerManagedKeyEncryption: list[CustomerManagedKeyEncryption]


    class azure.mgmt.eventgrid.types.KeyEncryptionKeyIdentity(TypedDict, total=False):
        key "type": Required[Union[str, KeyEncryptionIdentityType]]
        key "userAssignedIdentityResourceId": str
        type: Union[str, KeyEncryptionIdentityType]
        userAssignedIdentityResourceId: str


    class azure.mgmt.eventgrid.types.MonitorAlertEventSubscriptionDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[EndpointType.MONITOR_ALERT]]
        key "properties": ForwardRef('MonitorAlertEventSubscriptionDestinationProperties', module='types')
        endpointType: Literal[EndpointType.MONITOR_ALERT]
        properties: MonitorAlertEventSubscriptionDestinationProperties


    class azure.mgmt.eventgrid.types.MonitorAlertEventSubscriptionDestinationProperties(TypedDict, total=False):
        key "description": str
        key "severity": Union[str, MonitorAlertSeverity]
        actionGroups: list[str]
        description: str
        severity: Union[str, MonitorAlertSeverity]


    class azure.mgmt.eventgrid.types.Namespace(TrackedResource):
        key "id": str
        key "identity": ForwardRef('IdentityInfo', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NamespaceProperties', module='types')
        key "sku": ForwardRef('NamespaceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityInfo
        location: str
        name: str
        properties: NamespaceProperties
        sku: NamespaceSku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventgrid.types.NamespaceProperties(TypedDict, total=False):
        key "autoScaleConfiguration": ForwardRef('AutoScaleConfiguration', module='types')
        key "ipAddressType": Union[str, IpAddressType]
        key "isZoneRedundant": bool
        key "minimumTlsVersionAllowed": Union[str, TlsVersion]
        key "provisioningState": Union[str, NamespaceProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "topicSpacesConfiguration": ForwardRef('TopicSpacesConfiguration', module='types')
        key "topicsConfiguration": ForwardRef('TopicsConfiguration', module='types')
        autoScaleConfiguration: AutoScaleConfiguration
        inboundIpRules: list[InboundIpRule]
        ipAddressType: Union[str, IpAddressType]
        isZoneRedundant: bool
        minimumTlsVersionAllowed: Union[str, TlsVersion]
        privateEndpointConnections: list[PrivateEndpointConnection]
        provisioningState: Union[str, NamespaceProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        topicSpacesConfiguration: TopicSpacesConfiguration
        topicsConfiguration: TopicsConfiguration


    class azure.mgmt.eventgrid.types.NamespaceRegenerateKeyRequest(TypedDict, total=False):
        key "keyName": Required[str]
        keyName: str


    class azure.mgmt.eventgrid.types.NamespaceSku(TypedDict, total=False):
        key "capacity": int
        key "name": Union[str, SkuName]
        capacity: int
        name: Union[str, SkuName]


    class azure.mgmt.eventgrid.types.NamespaceTopic(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('NamespaceTopicProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: NamespaceTopicProperties
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.NamespaceTopicEventSubscriptionDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[EndpointType.NAMESPACE_TOPIC]]
        key "properties": ForwardRef('NamespaceTopicEventSubscriptionDestinationProperties', module='types')
        endpointType: Literal[EndpointType.NAMESPACE_TOPIC]
        properties: NamespaceTopicEventSubscriptionDestinationProperties


    class azure.mgmt.eventgrid.types.NamespaceTopicEventSubscriptionDestinationProperties(TypedDict, total=False):
        key "resourceId": str
        resourceId: str


    class azure.mgmt.eventgrid.types.NamespaceTopicProperties(TypedDict, total=False):
        key "eventRetentionInDays": int
        key "inputSchema": Union[str, EventInputSchema]
        key "provisioningState": Union[str, NamespaceTopicProvisioningState]
        key "publisherType": Union[str, PublisherType]
        eventRetentionInDays: int
        inputSchema: Union[str, EventInputSchema]
        provisioningState: Union[str, NamespaceTopicProvisioningState]
        publisherType: Union[str, PublisherType]


    class azure.mgmt.eventgrid.types.NamespaceTopicUpdateParameterProperties(TypedDict, total=False):
        key "eventRetentionInDays": int
        eventRetentionInDays: int


    class azure.mgmt.eventgrid.types.NamespaceTopicUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('NamespaceTopicUpdateParameterProperties', module='types')
        properties: NamespaceTopicUpdateParameterProperties


    class azure.mgmt.eventgrid.types.NamespaceUpdateParameterProperties(TypedDict, total=False):
        key "autoScaleConfiguration": ForwardRef('UpdateAutoScaleConfiguration', module='types')
        key "ipAddressType": Union[str, IpAddressType]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "topicSpacesConfiguration": ForwardRef('UpdateTopicSpacesConfigurationInfo', module='types')
        key "topicsConfiguration": ForwardRef('UpdateTopicsConfigurationInfo', module='types')
        autoScaleConfiguration: UpdateAutoScaleConfiguration
        inboundIpRules: list[InboundIpRule]
        ipAddressType: Union[str, IpAddressType]
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        topicSpacesConfiguration: UpdateTopicSpacesConfigurationInfo
        topicsConfiguration: UpdateTopicsConfigurationInfo


    class azure.mgmt.eventgrid.types.NamespaceUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('IdentityInfo', module='types')
        key "properties": ForwardRef('NamespaceUpdateParameterProperties', module='types')
        key "sku": ForwardRef('NamespaceSku', module='types')
        identity: IdentityInfo
        properties: NamespaceUpdateParameterProperties
        sku: NamespaceSku
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.NumberGreaterThanAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.NUMBER_GREATER_THAN]]
        key "value": float
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.NUMBER_GREATER_THAN]
        value: float


    class azure.mgmt.eventgrid.types.NumberGreaterThanFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.NUMBER_GREATER_THAN]]
        key "value": float
        key: str
        operatorType: Literal[FilterOperatorType.NUMBER_GREATER_THAN]
        value: float


    class azure.mgmt.eventgrid.types.NumberGreaterThanOrEqualsAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.NUMBER_GREATER_THAN_OR_EQUALS]]
        key "value": float
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.NUMBER_GREATER_THAN_OR_EQUALS]
        value: float


    class azure.mgmt.eventgrid.types.NumberGreaterThanOrEqualsFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.NUMBER_GREATER_THAN_OR_EQUALS]]
        key "value": float
        key: str
        operatorType: Literal[FilterOperatorType.NUMBER_GREATER_THAN_OR_EQUALS]
        value: float


    class azure.mgmt.eventgrid.types.NumberInAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.NUMBER_IN]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.NUMBER_IN]
        values: list[float]


    class azure.mgmt.eventgrid.types.NumberInFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.NUMBER_IN]]
        key: str
        operatorType: Literal[FilterOperatorType.NUMBER_IN]
        values: list[float]


    class azure.mgmt.eventgrid.types.NumberInRangeAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.NUMBER_IN_RANGE]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.NUMBER_IN_RANGE]
        values: list[list[float]]


    class azure.mgmt.eventgrid.types.NumberInRangeFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.NUMBER_IN_RANGE]]
        key: str
        operatorType: Literal[FilterOperatorType.NUMBER_IN_RANGE]
        values: list[list[float]]


    class azure.mgmt.eventgrid.types.NumberLessThanAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.NUMBER_LESS_THAN]]
        key "value": float
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.NUMBER_LESS_THAN]
        value: float


    class azure.mgmt.eventgrid.types.NumberLessThanFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.NUMBER_LESS_THAN]]
        key "value": float
        key: str
        operatorType: Literal[FilterOperatorType.NUMBER_LESS_THAN]
        value: float


    class azure.mgmt.eventgrid.types.NumberLessThanOrEqualsAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.NUMBER_LESS_THAN_OR_EQUALS]]
        key "value": float
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.NUMBER_LESS_THAN_OR_EQUALS]
        value: float


    class azure.mgmt.eventgrid.types.NumberLessThanOrEqualsFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.NUMBER_LESS_THAN_OR_EQUALS]]
        key "value": float
        key: str
        operatorType: Literal[FilterOperatorType.NUMBER_LESS_THAN_OR_EQUALS]
        value: float


    class azure.mgmt.eventgrid.types.NumberNotInAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.NUMBER_NOT_IN]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.NUMBER_NOT_IN]
        values: list[float]


    class azure.mgmt.eventgrid.types.NumberNotInFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.NUMBER_NOT_IN]]
        key: str
        operatorType: Literal[FilterOperatorType.NUMBER_NOT_IN]
        values: list[float]


    class azure.mgmt.eventgrid.types.NumberNotInRangeAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.NUMBER_NOT_IN_RANGE]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.NUMBER_NOT_IN_RANGE]
        values: list[list[float]]


    class azure.mgmt.eventgrid.types.NumberNotInRangeFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.NUMBER_NOT_IN_RANGE]]
        key: str
        operatorType: Literal[FilterOperatorType.NUMBER_NOT_IN_RANGE]
        values: list[list[float]]


    class azure.mgmt.eventgrid.types.Partner(TypedDict, total=False):
        key "authorizationExpirationTimeInUtc": str
        key "partnerName": str
        key "partnerRegistrationImmutableId": str
        authorizationExpirationTimeInUtc: str
        partnerName: str
        partnerRegistrationImmutableId: str


    class azure.mgmt.eventgrid.types.PartnerAuthorization(TypedDict, total=False):
        key "defaultMaximumExpirationTimeInDays": int
        authorizedPartnersList: list[Partner]
        defaultMaximumExpirationTimeInDays: int


    class azure.mgmt.eventgrid.types.PartnerClientAuthentication(TypedDict, total=False):
        key "clientAuthenticationType": Required[Literal[PartnerClientAuthenticationType.AZURE_AD]]
        key "properties": ForwardRef('AzureADPartnerClientAuthenticationProperties', module='types')
        clientAuthenticationType: Literal[PartnerClientAuthenticationType.AZURE_AD]
        properties: AzureADPartnerClientAuthenticationProperties


    class azure.mgmt.eventgrid.types.PartnerClientAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_AD = "AzureAD"


    class azure.mgmt.eventgrid.types.PartnerConfiguration(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('PartnerConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PartnerConfigurationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventgrid.types.PartnerConfigurationProperties(TypedDict, total=False):
        key "partnerAuthorization": ForwardRef('PartnerAuthorization', module='types')
        key "provisioningState": Union[str, PartnerConfigurationProvisioningState]
        partnerAuthorization: PartnerAuthorization
        provisioningState: Union[str, PartnerConfigurationProvisioningState]


    class azure.mgmt.eventgrid.types.PartnerConfigurationUpdateParameterProperties(TypedDict, total=False):
        key "defaultMaximumExpirationTimeInDays": int
        defaultMaximumExpirationTimeInDays: int


    class azure.mgmt.eventgrid.types.PartnerConfigurationUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('PartnerConfigurationUpdateParameterProperties', module='types')
        properties: PartnerConfigurationUpdateParameterProperties
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.PartnerDestination(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PartnerDestinationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PartnerDestinationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventgrid.types.PartnerDestinationInfo(TypedDict, total=False):
        key "azureSubscriptionId": str
        key "endpointServiceContext": str
        key "endpointType": Required[Literal[PartnerEndpointType.WEB_HOOK]]
        key "name": str
        key "properties": ForwardRef('WebhookPartnerDestinationProperties', module='types')
        key "resourceGroupName": str
        azureSubscriptionId: str
        endpointServiceContext: str
        endpointType: Literal[PartnerEndpointType.WEB_HOOK]
        name: str
        properties: WebhookPartnerDestinationProperties
        resourceGroupName: str
        resourceMoveChangeHistory: list[ResourceMoveChangeHistory]


    class azure.mgmt.eventgrid.types.PartnerDestinationProperties(TypedDict, total=False):
        key "activationState": Union[str, PartnerDestinationActivationState]
        key "endpointBaseUrl": str
        key "endpointServiceContext": str
        key "expirationTimeIfNotActivatedUtc": str
        key "messageForActivation": str
        key "partnerRegistrationImmutableId": str
        key "provisioningState": Union[str, PartnerDestinationProvisioningState]
        activationState: Union[str, PartnerDestinationActivationState]
        endpointBaseUrl: str
        endpointServiceContext: str
        expirationTimeIfNotActivatedUtc: str
        messageForActivation: str
        partnerRegistrationImmutableId: str
        provisioningState: Union[str, PartnerDestinationProvisioningState]


    class azure.mgmt.eventgrid.types.PartnerDestinationUpdateParameters(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.PartnerEndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEB_HOOK = "WebHook"


    class azure.mgmt.eventgrid.types.PartnerEventSubscriptionDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[EndpointType.PARTNER_DESTINATION]]
        key "properties": ForwardRef('PartnerEventSubscriptionDestinationProperties', module='types')
        endpointType: Literal[EndpointType.PARTNER_DESTINATION]
        properties: PartnerEventSubscriptionDestinationProperties


    class azure.mgmt.eventgrid.types.PartnerEventSubscriptionDestinationProperties(TypedDict, total=False):
        key "resourceId": str
        resourceId: str


    class azure.mgmt.eventgrid.types.PartnerNamespace(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PartnerNamespaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PartnerNamespaceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventgrid.types.PartnerNamespaceProperties(TypedDict, total=False):
        key "disableLocalAuth": bool
        key "endpoint": str
        key "minimumTlsVersionAllowed": Union[str, TlsVersion]
        key "partnerRegistrationFullyQualifiedId": str
        key "partnerTopicRoutingMode": Union[str, PartnerTopicRoutingMode]
        key "provisioningState": Union[str, PartnerNamespaceProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        disableLocalAuth: bool
        endpoint: str
        inboundIpRules: list[InboundIpRule]
        minimumTlsVersionAllowed: Union[str, TlsVersion]
        partnerRegistrationFullyQualifiedId: str
        partnerTopicRoutingMode: Union[str, PartnerTopicRoutingMode]
        privateEndpointConnections: list[PrivateEndpointConnection]
        provisioningState: Union[str, PartnerNamespaceProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]


    class azure.mgmt.eventgrid.types.PartnerNamespaceRegenerateKeyRequest(TypedDict, total=False):
        key "keyName": Required[str]
        keyName: str


    class azure.mgmt.eventgrid.types.PartnerNamespaceUpdateParameterProperties(TypedDict, total=False):
        key "disableLocalAuth": bool
        key "minimumTlsVersionAllowed": Union[str, TlsVersion]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        disableLocalAuth: bool
        inboundIpRules: list[InboundIpRule]
        minimumTlsVersionAllowed: Union[str, TlsVersion]
        publicNetworkAccess: Union[str, PublicNetworkAccess]


    class azure.mgmt.eventgrid.types.PartnerNamespaceUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('PartnerNamespaceUpdateParameterProperties', module='types')
        properties: PartnerNamespaceUpdateParameterProperties
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.PartnerRegistration(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PartnerRegistrationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PartnerRegistrationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventgrid.types.PartnerRegistrationProperties(TypedDict, total=False):
        key "partnerRegistrationImmutableId": str
        key "provisioningState": Union[str, PartnerRegistrationProvisioningState]
        partnerRegistrationImmutableId: str
        provisioningState: Union[str, PartnerRegistrationProvisioningState]


    class azure.mgmt.eventgrid.types.PartnerRegistrationUpdateParameters(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.PartnerTopic(TrackedResource):
        key "id": str
        key "identity": ForwardRef('IdentityInfo', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PartnerTopicProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityInfo
        location: str
        name: str
        properties: PartnerTopicProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventgrid.types.PartnerTopicInfo(TypedDict, total=False):
        key "azureSubscriptionId": str
        key "eventTypeInfo": ForwardRef('EventTypeInfo', module='types')
        key "name": str
        key "resourceGroupName": str
        key "source": str
        azureSubscriptionId: str
        eventTypeInfo: EventTypeInfo
        name: str
        resourceGroupName: str
        source: str


    class azure.mgmt.eventgrid.types.PartnerTopicProperties(TypedDict, total=False):
        key "activationState": Union[str, PartnerTopicActivationState]
        key "eventTypeInfo": ForwardRef('EventTypeInfo', module='types')
        key "expirationTimeIfNotActivatedUtc": str
        key "messageForActivation": str
        key "partnerRegistrationImmutableId": str
        key "partnerTopicFriendlyDescription": str
        key "provisioningState": Union[str, PartnerTopicProvisioningState]
        key "source": str
        activationState: Union[str, PartnerTopicActivationState]
        eventTypeInfo: EventTypeInfo
        expirationTimeIfNotActivatedUtc: str
        messageForActivation: str
        partnerRegistrationImmutableId: str
        partnerTopicFriendlyDescription: str
        provisioningState: Union[str, PartnerTopicProvisioningState]
        source: str


    class azure.mgmt.eventgrid.types.PartnerTopicUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('IdentityInfo', module='types')
        identity: IdentityInfo
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.PartnerUpdateDestinationInfo(TypedDict, total=False):
        key "endpointType": Required[Literal[PartnerEndpointType.WEB_HOOK]]
        key "properties": ForwardRef('WebhookPartnerDestinationProperties', module='types')
        endpointType: Literal[PartnerEndpointType.WEB_HOOK]
        properties: WebhookPartnerDestinationProperties


    class azure.mgmt.eventgrid.types.PartnerUpdateTopicInfo(TypedDict, total=False):
        key "eventTypeInfo": ForwardRef('EventTypeInfo', module='types')
        eventTypeInfo: EventTypeInfo


    class azure.mgmt.eventgrid.types.PermissionBinding(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PermissionBindingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PermissionBindingProperties
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.PermissionBindingProperties(TypedDict, total=False):
        key "clientGroupName": str
        key "description": str
        key "permission": Union[str, PermissionType]
        key "provisioningState": Union[str, PermissionBindingProvisioningState]
        key "topicSpaceName": str
        clientGroupName: str
        description: str
        permission: Union[str, PermissionType]
        provisioningState: Union[str, PermissionBindingProvisioningState]
        topicSpaceName: str


    class azure.mgmt.eventgrid.types.PlatformCapabilities(TypedDict, total=False):
        key "confidentialCompute": ForwardRef('ConfidentialCompute', module='types')
        confidentialCompute: ConfidentialCompute


    class azure.mgmt.eventgrid.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.eventgrid.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('ConnectionState', module='types')
        key "provisioningState": Union[str, ResourceProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: ConnectionState
        provisioningState: Union[str, ResourceProvisioningState]


    class azure.mgmt.eventgrid.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.PushInfo(TypedDict, total=False):
        key "deadLetterDestinationWithResourceIdentity": ForwardRef('DeadLetterWithResourceIdentity', module='types')
        key "deliveryWithResourceIdentity": ForwardRef('DeliveryWithResourceIdentity', module='types')
        key "destination": ForwardRef('EventSubscriptionDestination', module='types')
        key "eventTimeToLive": str
        key "maxDeliveryCount": int
        deadLetterDestinationWithResourceIdentity: DeadLetterWithResourceIdentity
        deliveryWithResourceIdentity: DeliveryWithResourceIdentity
        destination: EventSubscriptionDestination
        eventTimeToLive: str
        maxDeliveryCount: int


    class azure.mgmt.eventgrid.types.QueueInfo(TypedDict, total=False):
        key "deadLetterDestinationWithResourceIdentity": ForwardRef('DeadLetterWithResourceIdentity', module='types')
        key "eventTimeToLive": str
        key "maxDeliveryCount": int
        key "receiveLockDurationInSeconds": int
        deadLetterDestinationWithResourceIdentity: DeadLetterWithResourceIdentity
        eventTimeToLive: str
        maxDeliveryCount: int
        receiveLockDurationInSeconds: int


    class azure.mgmt.eventgrid.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.ResourceMoveChangeHistory(TypedDict, total=False):
        key "azureSubscriptionId": str
        key "changedTimeUtc": str
        key "resourceGroupName": str
        azureSubscriptionId: str
        changedTimeUtc: str
        resourceGroupName: str


    class azure.mgmt.eventgrid.types.ResourceSku(TypedDict, total=False):
        key "name": Union[str, Sku]
        name: Union[str, Sku]


    class azure.mgmt.eventgrid.types.RetryPolicy(TypedDict, total=False):
        key "eventTimeToLiveInMinutes": int
        key "maxDeliveryAttempts": int
        eventTimeToLiveInMinutes: int
        maxDeliveryAttempts: int


    class azure.mgmt.eventgrid.types.RoutingEnrichments(TypedDict, total=False):
        dynamic: list[DynamicRoutingEnrichment]
        static: list[StaticRoutingEnrichment]


    class azure.mgmt.eventgrid.types.RoutingIdentityInfo(TypedDict, total=False):
        key "type": Union[str, RoutingIdentityType]
        key "userAssignedIdentity": str
        type: Union[str, RoutingIdentityType]
        userAssignedIdentity: str


    class azure.mgmt.eventgrid.types.ServiceBusQueueEventSubscriptionDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[EndpointType.SERVICE_BUS_QUEUE]]
        key "properties": ForwardRef('ServiceBusQueueEventSubscriptionDestinationProperties', module='types')
        endpointType: Literal[EndpointType.SERVICE_BUS_QUEUE]
        properties: ServiceBusQueueEventSubscriptionDestinationProperties


    class azure.mgmt.eventgrid.types.ServiceBusQueueEventSubscriptionDestinationProperties(TypedDict, total=False):
        key "resourceId": str
        deliveryAttributeMappings: list[DeliveryAttributeMapping]
        resourceId: str


    class azure.mgmt.eventgrid.types.ServiceBusTopicEventSubscriptionDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[EndpointType.SERVICE_BUS_TOPIC]]
        key "properties": ForwardRef('ServiceBusTopicEventSubscriptionDestinationProperties', module='types')
        endpointType: Literal[EndpointType.SERVICE_BUS_TOPIC]
        properties: ServiceBusTopicEventSubscriptionDestinationProperties


    class azure.mgmt.eventgrid.types.ServiceBusTopicEventSubscriptionDestinationProperties(TypedDict, total=False):
        key "resourceId": str
        deliveryAttributeMappings: list[DeliveryAttributeMapping]
        resourceId: str


    class azure.mgmt.eventgrid.types.StaticDeliveryAttributeMapping(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('StaticDeliveryAttributeMappingProperties', module='types')
        key "type": Required[Literal[DeliveryAttributeMappingType.STATIC]]
        name: str
        properties: StaticDeliveryAttributeMappingProperties
        type: Literal[DeliveryAttributeMappingType.STATIC]


    class azure.mgmt.eventgrid.types.StaticDeliveryAttributeMappingProperties(TypedDict, total=False):
        key "isSecret": bool
        key "value": str
        isSecret: bool
        value: str


    class azure.mgmt.eventgrid.types.StaticRoutingEnrichment(TypedDict, total=False):
        key "key": str
        key "value": str
        key "valueType": Required[Literal[StaticRoutingEnrichmentType.STRING]]
        key: str
        value: str
        valueType: Literal[StaticRoutingEnrichmentType.STRING]


    class azure.mgmt.eventgrid.types.StaticRoutingEnrichmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STRING = "String"


    class azure.mgmt.eventgrid.types.StaticStringRoutingEnrichment(TypedDict, total=False):
        key "key": str
        key "value": str
        key "valueType": Required[Literal[StaticRoutingEnrichmentType.STRING]]
        key: str
        value: str
        valueType: Literal[StaticRoutingEnrichmentType.STRING]


    class azure.mgmt.eventgrid.types.StorageBlobDeadLetterDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[DeadLetterEndPointType.STORAGE_BLOB]]
        key "properties": ForwardRef('StorageBlobDeadLetterDestinationProperties', module='types')
        endpointType: Literal[DeadLetterEndPointType.STORAGE_BLOB]
        properties: StorageBlobDeadLetterDestinationProperties


    class azure.mgmt.eventgrid.types.StorageBlobDeadLetterDestinationProperties(TypedDict, total=False):
        key "blobContainerName": str
        key "resourceId": str
        blobContainerName: str
        resourceId: str


    class azure.mgmt.eventgrid.types.StorageQueueEventSubscriptionDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[EndpointType.STORAGE_QUEUE]]
        key "properties": ForwardRef('StorageQueueEventSubscriptionDestinationProperties', module='types')
        endpointType: Literal[EndpointType.STORAGE_QUEUE]
        properties: StorageQueueEventSubscriptionDestinationProperties


    class azure.mgmt.eventgrid.types.StorageQueueEventSubscriptionDestinationProperties(TypedDict, total=False):
        key "queueMessageTimeToLiveInSeconds": int
        key "queueName": str
        key "resourceId": str
        queueMessageTimeToLiveInSeconds: int
        queueName: str
        resourceId: str


    class azure.mgmt.eventgrid.types.StringBeginsWithAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.STRING_BEGINS_WITH]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.STRING_BEGINS_WITH]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringBeginsWithFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.STRING_BEGINS_WITH]]
        key: str
        operatorType: Literal[FilterOperatorType.STRING_BEGINS_WITH]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringContainsAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.STRING_CONTAINS]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.STRING_CONTAINS]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringContainsFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.STRING_CONTAINS]]
        key: str
        operatorType: Literal[FilterOperatorType.STRING_CONTAINS]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringEndsWithAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.STRING_ENDS_WITH]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.STRING_ENDS_WITH]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringEndsWithFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.STRING_ENDS_WITH]]
        key: str
        operatorType: Literal[FilterOperatorType.STRING_ENDS_WITH]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringInAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.STRING_IN]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.STRING_IN]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringInFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.STRING_IN]]
        key: str
        operatorType: Literal[FilterOperatorType.STRING_IN]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringNotBeginsWithAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.STRING_NOT_BEGINS_WITH]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.STRING_NOT_BEGINS_WITH]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringNotBeginsWithFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.STRING_NOT_BEGINS_WITH]]
        key: str
        operatorType: Literal[FilterOperatorType.STRING_NOT_BEGINS_WITH]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringNotContainsAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.STRING_NOT_CONTAINS]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.STRING_NOT_CONTAINS]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringNotContainsFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.STRING_NOT_CONTAINS]]
        key: str
        operatorType: Literal[FilterOperatorType.STRING_NOT_CONTAINS]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringNotEndsWithAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.STRING_NOT_ENDS_WITH]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.STRING_NOT_ENDS_WITH]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringNotEndsWithFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.STRING_NOT_ENDS_WITH]]
        key: str
        operatorType: Literal[FilterOperatorType.STRING_NOT_ENDS_WITH]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringNotInAdvancedFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[AdvancedFilterOperatorType.STRING_NOT_IN]]
        key: str
        operatorType: Literal[AdvancedFilterOperatorType.STRING_NOT_IN]
        values: list[str]


    class azure.mgmt.eventgrid.types.StringNotInFilter(TypedDict, total=False):
        key "key": str
        key "operatorType": Required[Literal[FilterOperatorType.STRING_NOT_IN]]
        key: str
        operatorType: Literal[FilterOperatorType.STRING_NOT_IN]
        values: list[str]


    class azure.mgmt.eventgrid.types.Subscription(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SubscriptionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SubscriptionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.SubscriptionProperties(TypedDict, total=False):
        key "deliveryConfiguration": ForwardRef('DeliveryConfiguration', module='types')
        key "eventDeliverySchema": Union[str, DeliverySchema]
        key "expirationTimeUtc": str
        key "filtersConfiguration": ForwardRef('FiltersConfiguration', module='types')
        key "provisioningState": Union[str, SubscriptionProvisioningState]
        deliveryConfiguration: DeliveryConfiguration
        eventDeliverySchema: Union[str, DeliverySchema]
        expirationTimeUtc: str
        filtersConfiguration: FiltersConfiguration
        provisioningState: Union[str, SubscriptionProvisioningState]
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.SubscriptionUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('SubscriptionUpdateParametersProperties', module='types')
        properties: SubscriptionUpdateParametersProperties


    class azure.mgmt.eventgrid.types.SubscriptionUpdateParametersProperties(TypedDict, total=False):
        key "deliveryConfiguration": ForwardRef('DeliveryConfiguration', module='types')
        key "eventDeliverySchema": Union[str, DeliverySchema]
        key "expirationTimeUtc": str
        key "filtersConfiguration": ForwardRef('FiltersConfiguration', module='types')
        deliveryConfiguration: DeliveryConfiguration
        eventDeliverySchema: Union[str, DeliverySchema]
        expirationTimeUtc: str
        filtersConfiguration: FiltersConfiguration
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.eventgrid.types.SystemTopic(TrackedResource):
        key "id": str
        key "identity": ForwardRef('IdentityInfo', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SystemTopicProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityInfo
        location: str
        name: str
        properties: SystemTopicProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventgrid.types.SystemTopicProperties(TypedDict, total=False):
        key "encryption": ForwardRef('KeyEncryption', module='types')
        key "metricResourceId": str
        key "platformCapabilities": ForwardRef('PlatformCapabilities', module='types')
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "source": str
        key "topicType": str
        encryption: KeyEncryption
        metricResourceId: str
        platformCapabilities: PlatformCapabilities
        provisioningState: Union[str, ResourceProvisioningState]
        source: str
        topicType: str


    class azure.mgmt.eventgrid.types.SystemTopicUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('IdentityInfo', module='types')
        identity: IdentityInfo
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.Topic(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "identity": ForwardRef('IdentityInfo', module='types')
        key "kind": Union[str, ResourceKind]
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('TopicProperties', module='types')
        key "sku": ForwardRef('ResourceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        identity: IdentityInfo
        kind: Union[str, ResourceKind]
        location: str
        name: str
        properties: TopicProperties
        sku: ResourceSku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventgrid.types.TopicProperties(TypedDict, total=False):
        key "dataResidencyBoundary": Union[str, DataResidencyBoundary]
        key "disableLocalAuth": bool
        key "encryption": ForwardRef('KeyEncryption', module='types')
        key "endpoint": str
        key "eventTypeInfo": ForwardRef('EventTypeInfo', module='types')
        key "inputSchema": Union[str, InputSchema]
        key "inputSchemaMapping": ForwardRef('InputSchemaMapping', module='types')
        key "metricResourceId": str
        key "minimumTlsVersionAllowed": Union[str, TlsVersion]
        key "platformCapabilities": ForwardRef('PlatformCapabilities', module='types')
        key "provisioningState": Union[str, TopicProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        dataResidencyBoundary: Union[str, DataResidencyBoundary]
        disableLocalAuth: bool
        encryption: KeyEncryption
        endpoint: str
        eventTypeInfo: EventTypeInfo
        inboundIpRules: list[InboundIpRule]
        inputSchema: Union[str, InputSchema]
        inputSchemaMapping: InputSchemaMapping
        metricResourceId: str
        minimumTlsVersionAllowed: Union[str, TlsVersion]
        platformCapabilities: PlatformCapabilities
        privateEndpointConnections: list[PrivateEndpointConnection]
        provisioningState: Union[str, TopicProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]


    class azure.mgmt.eventgrid.types.TopicRegenerateKeyRequest(TypedDict, total=False):
        key "keyName": Required[str]
        keyName: str


    class azure.mgmt.eventgrid.types.TopicSpace(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TopicSpaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TopicSpaceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.eventgrid.types.TopicSpaceProperties(TypedDict, total=False):
        key "description": str
        key "provisioningState": Union[str, TopicSpaceProvisioningState]
        description: str
        provisioningState: Union[str, TopicSpaceProvisioningState]
        topicTemplates: list[str]


    class azure.mgmt.eventgrid.types.TopicSpacesConfiguration(TypedDict, total=False):
        key "clientAuthentication": ForwardRef('ClientAuthenticationSettings', module='types')
        key "hostname": str
        key "maximumClientSessionsPerAuthenticationName": int
        key "maximumSessionExpiryInHours": int
        key "routeTopicResourceId": str
        key "routingEnrichments": ForwardRef('RoutingEnrichments', module='types')
        key "routingIdentityInfo": ForwardRef('RoutingIdentityInfo', module='types')
        key "state": Union[str, TopicSpacesConfigurationState]
        clientAuthentication: ClientAuthenticationSettings
        customDomains: list[CustomDomainConfiguration]
        hostname: str
        maximumClientSessionsPerAuthenticationName: int
        maximumSessionExpiryInHours: int
        routeTopicResourceId: str
        routingEnrichments: RoutingEnrichments
        routingIdentityInfo: RoutingIdentityInfo
        state: Union[str, TopicSpacesConfigurationState]


    class azure.mgmt.eventgrid.types.TopicUpdateParameterProperties(TypedDict, total=False):
        key "dataResidencyBoundary": Union[str, DataResidencyBoundary]
        key "disableLocalAuth": bool
        key "eventTypeInfo": ForwardRef('EventTypeInfo', module='types')
        key "minimumTlsVersionAllowed": Union[str, TlsVersion]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        dataResidencyBoundary: Union[str, DataResidencyBoundary]
        disableLocalAuth: bool
        eventTypeInfo: EventTypeInfo
        inboundIpRules: list[InboundIpRule]
        minimumTlsVersionAllowed: Union[str, TlsVersion]
        publicNetworkAccess: Union[str, PublicNetworkAccess]


    class azure.mgmt.eventgrid.types.TopicUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('IdentityInfo', module='types')
        key "properties": ForwardRef('TopicUpdateParameterProperties', module='types')
        key "sku": ForwardRef('ResourceSku', module='types')
        identity: IdentityInfo
        properties: TopicUpdateParameterProperties
        sku: ResourceSku
        tags: dict[str, str]


    class azure.mgmt.eventgrid.types.TopicsConfiguration(TypedDict, total=False):
        key "hostname": str
        customDomains: list[CustomDomainConfiguration]
        hostname: str


    class azure.mgmt.eventgrid.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventgrid.types.UpdateAutoScaleConfiguration(TypedDict, total=False):
        key "enableAutoScale": bool
        key "maximumThroughputUnits": int
        key "minimumThroughputUnits": int
        enableAutoScale: bool
        maximumThroughputUnits: int
        minimumThroughputUnits: int


    class azure.mgmt.eventgrid.types.UpdateTopicSpacesConfigurationInfo(TypedDict, total=False):
        key "clientAuthentication": ForwardRef('ClientAuthenticationSettings', module='types')
        key "maximumClientSessionsPerAuthenticationName": int
        key "maximumSessionExpiryInHours": int
        key "routeTopicResourceId": str
        key "routingEnrichments": ForwardRef('RoutingEnrichments', module='types')
        key "routingIdentityInfo": ForwardRef('RoutingIdentityInfo', module='types')
        key "state": Union[str, TopicSpacesConfigurationState]
        clientAuthentication: ClientAuthenticationSettings
        customDomains: list[CustomDomainConfiguration]
        maximumClientSessionsPerAuthenticationName: int
        maximumSessionExpiryInHours: int
        routeTopicResourceId: str
        routingEnrichments: RoutingEnrichments
        routingIdentityInfo: RoutingIdentityInfo
        state: Union[str, TopicSpacesConfigurationState]


    class azure.mgmt.eventgrid.types.UpdateTopicsConfigurationInfo(TypedDict, total=False):
        customDomains: list[CustomDomainConfiguration]


    class azure.mgmt.eventgrid.types.UserIdentityProperties(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.eventgrid.types.WebHookEventSubscriptionDestination(TypedDict, total=False):
        key "endpointType": Required[Literal[EndpointType.WEB_HOOK]]
        key "properties": ForwardRef('WebHookEventSubscriptionDestinationProperties', module='types')
        endpointType: Literal[EndpointType.WEB_HOOK]
        properties: WebHookEventSubscriptionDestinationProperties


    class azure.mgmt.eventgrid.types.WebHookEventSubscriptionDestinationProperties(TypedDict, total=False):
        key "azureActiveDirectoryApplicationIdOrUri": str
        key "azureActiveDirectoryTenantId": str
        key "endpointBaseUrl": str
        key "endpointUrl": str
        key "maxEventsPerBatch": int
        key "minimumTlsVersionAllowed": Union[str, TlsVersion]
        key "preferredBatchSizeInKilobytes": int
        azureActiveDirectoryApplicationIdOrUri: str
        azureActiveDirectoryTenantId: str
        deliveryAttributeMappings: list[DeliveryAttributeMapping]
        endpointBaseUrl: str
        endpointUrl: str
        maxEventsPerBatch: int
        minimumTlsVersionAllowed: Union[str, TlsVersion]
        preferredBatchSizeInKilobytes: int


    class azure.mgmt.eventgrid.types.WebhookAuthenticationSettings(TypedDict, total=False):
        key "azureActiveDirectoryApplicationIdOrUri": Required[str]
        key "azureActiveDirectoryTenantId": Required[str]
        key "endpointBaseUrl": str
        key "endpointUrl": Required[str]
        key "identity": Required[CustomWebhookAuthenticationManagedIdentity]
        azureActiveDirectoryApplicationIdOrUri: str
        azureActiveDirectoryTenantId: str
        endpointBaseUrl: str
        endpointUrl: str
        identity: CustomWebhookAuthenticationManagedIdentity


    class azure.mgmt.eventgrid.types.WebhookPartnerDestinationInfo(TypedDict, total=False):
        key "azureSubscriptionId": str
        key "endpointServiceContext": str
        key "endpointType": Required[Literal[PartnerEndpointType.WEB_HOOK]]
        key "name": str
        key "properties": ForwardRef('WebhookPartnerDestinationProperties', module='types')
        key "resourceGroupName": str
        azureSubscriptionId: str
        endpointServiceContext: str
        endpointType: Literal[PartnerEndpointType.WEB_HOOK]
        name: str
        properties: WebhookPartnerDestinationProperties
        resourceGroupName: str
        resourceMoveChangeHistory: list[ResourceMoveChangeHistory]


    class azure.mgmt.eventgrid.types.WebhookPartnerDestinationProperties(TypedDict, total=False):
        key "clientAuthentication": ForwardRef('PartnerClientAuthentication', module='types')
        key "endpointBaseUrl": str
        key "endpointUrl": str
        clientAuthentication: PartnerClientAuthentication
        endpointBaseUrl: str
        endpointUrl: str


    class azure.mgmt.eventgrid.types.WebhookUpdatePartnerDestinationInfo(TypedDict, total=False):
        key "endpointType": Required[Literal[PartnerEndpointType.WEB_HOOK]]
        key "properties": ForwardRef('WebhookPartnerDestinationProperties', module='types')
        endpointType: Literal[PartnerEndpointType.WEB_HOOK]
        properties: WebhookPartnerDestinationProperties


```